"""ChatKit Server implementation for Todoly task management.

This module provides the ChatKit server that bridges the ChatKit frontend
with our OpenAI Agents SDK + FastMCP + LiteLLM backend.
"""

from typing import Any, AsyncIterator

import httpx
from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStreamableHttp
from agents.extensions.models.litellm_model import LitellmModel
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    ClientToolCallItem,
    ErrorEvent,
    ThreadMetadata,
    UserMessageItem,
)

from src.core.chatkit_store import NeonChatKitStore
from src.core.logging import get_logger
from src.config import settings

logger = get_logger(__name__)

# Frontend URL for revalidation calls
FRONTEND_URL = settings.FRONTEND_URL or "http://localhost:3000"


def sanitize_json_arguments(text: str) -> str:
    """Fix common JSON formatting issues from Nebius/qwen model.

    This addresses issues like:
    - Leading colons: ": {"user_id": "..."}
    - Trailing colons: "{"user_id": "..."}:"
    - Trailing commas in arrays
    - Missing quotes around keys
    - Missing quotes around string values

    Args:
        text: Raw text that may contain JSON arguments

    Returns:
        Sanitized JSON string
    """
    import re

    # Find JSON-like content between curly braces
    # Look for patterns like: key: value or "key": "value"
    json_pattern = r'\{[^{}]*\}'
    matches = list(re.finditer(json_pattern, text))

    if not matches:
        return text

    # Process each JSON-like block
    result = text
    for match in reversed(matches):
        original = match.group()
        sanitized = _sanitize_json_block(original)
        if sanitized != original:
            result = result[:match.start()] + sanitized + result[match.end():]

    return result


def _sanitize_json_block(block: str) -> str:
    """Sanitize a single JSON block."""
    import re

    # Remove leading/trailing whitespace
    block = block.strip()

    # Remove leading colon if present (common Nebius error)
    block = re.sub(r'^:\s*', '', block)

    # Remove trailing colon if present
    block = re.sub(r':\s*$', '', block)

    # Ensure it starts with { and ends with }
    if not block.startswith('{'):
        # Try to find JSON start
        json_start = block.find('{')
        if json_start != -1:
            block = block[json_start:]
    if not block.endswith('}'):
        # Try to find JSON end
        json_end = block.rfind('}')
        if json_end != -1:
            block = block[:json_end + 1]

    # If still not valid JSON, return original
    if not (block.startswith('{') and block.endswith('}')):
        return block

    # Fix: add quotes around unquoted keys (e.g., {user_id: "..."} -> {"user_id": "..."})
    block = re.sub(
        r'\{(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):',
        r'{\1"\2"\3:',
        block
    )

    # Fix: add quotes around unquoted string values that are simple words
    # This is trickier - we need to avoid matching numbers, booleans, null
    # Match: key followed by unquoted word (not true/false/null/number)
    def fix_unquoted_value(match):
        before = match.group(1)
        value = match.group(2)
        after = match.group(3)
        # Don't quote if it looks like a number or boolean
        if value.lower() in ('true', 'false', 'null') or re.match(r'^-?\d+(\.\d+)?$', value):
            return match.group(0)
        return f'{before}"{value}"{after}'

    # Only apply if the value isn't already quoted
    # Match colon followed by word character not preceded by quote
    block = re.sub(
        r'(:\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])',
        fix_unquoted_value,
        block
    )

    return block


async def trigger_frontend_revalidation(action: str = "update") -> None:
    """Trigger on-demand revalidation on the Next.js frontend.

    This function calls the Next.js API route to invalidate the task cache
    after the chatbot makes changes to tasks.

    Args:
        action: The action that triggered revalidation (create, update, delete, etc.)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/revalidate/tasks",
                json={"action": action},
                timeout=10.0,
            )
            if response.status_code == 200:
                logger.info(f"✅ Frontend revalidation triggered after {action}")
            else:
                logger.warning(
                    f"⚠️ Frontend revalidation failed: {response.status_code} - {response.text}"
                )
    except httpx.RequestError as e:
        logger.warning(f"⚠️ Could not trigger frontend revalidation: {e}")
    except Exception as e:
        logger.error(f"❌ Error triggering frontend revalidation: {e}", exc_info=True)


# Title generation agent - creates concise thread titles from user's first message
# Using OpenRouter instead of Gemini to avoid rate limits
title_agent = Agent(
    name="Thread Title Generator",
    instructions="""You generate concise, descriptive titles for chat conversations.
    Based on the user's first message, create a short title (3-6 words) that captures the main topic.

    Examples:
    - User: "Add a task to buy groceries" → Title: "Grocery Shopping Task"
    - User: "What tasks do I have today?" → Title: "Today's Tasks"
    - User: "Create a high priority work task" → Title: "High Priority Work Task"

    Return ONLY the title text, nothing else.""",
    model=LitellmModel(
        model="openrouter/qwen/qwen3-coder",
        api_key=settings.OPENROUTER_API_KEY,
    ),
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=50,
    ),
)


class TodolyChatKitServer(ChatKitServer):
    """ChatKit server implementation for Todoly task management.

    This server integrates:
    - ChatKit frontend for React UI
    - NeonChatKitStore for PostgreSQL persistence
    - OpenAI Agents SDK for agent orchestration
    - LiteLLM for multi-provider LLM access (GLM-4.5-air)
    - FastMCP for task management tool exposure
    """

    def __init__(self, database_url: str):
        """Initialize the ChatKit server.

        Args:
            database_url: PostgreSQL connection string for Neon database
        """
        if not database_url:
            raise ValueError("DATABASE_URL is required")

        # Initialize with Neon database store for persistent chat history
        super().__init__(store=NeonChatKitStore(database_url))

        # Agent will be created per request

    async def _create_agent_with_mcp(self, user_id: str) -> tuple[Agent, Any]:
        """Create and configure the agent with FastMCP server.

        Args:
            user_id: Authenticated user ID to pass to MCP tools

        Returns:
            Tuple of (Agent instance, MCP server instance)
        """
        # Create MCP server connection
        mcp_server = MCPServerStreamableHttp(
            name="Task Management Server",
            params={
                "url": settings.MCP_SERVER_URL,
                "headers": {"Authorization": f"Bearer {settings.MCP_SERVER_TOKEN}"},
                "timeout": 30,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        )

        # Connect to MCP server before creating agent
        await mcp_server.connect()
        logger.info("Connected to MCP server: %s", settings.MCP_SERVER_URL)

        # Create task management agent with MCP server
        agent = Agent(
            name="TaskBot",
            instructions=f"""You are a task management assistant for a todo app. You help users manage their tasks through natural conversation.

## CRITICAL RULES:
1. You MUST use MCP tools for ALL task operations - NEVER fabricate task IDs or responses
2. ALWAYS pass user_id="{user_id}" to EVERY tool call
3. Use COMPLETE task IDs from tool results - NEVER guess or use partial IDs
4. Wait for tool responses before responding to the user
5. **AFTER TOOL CALLS: Use ONLY the tool's "message" field - do NOT add any additional text!**

## TOOL CALL RULES - FOLLOW EXACTLY:

### TOOL CALL ARGUMENTS MUST BE CLEAN JSON:
When the system asks for tool arguments, output ONLY valid JSON.
Example for list_tasks: {{"user_id": "{user_id}", "status": "pending"}}
Example for add_task: {{"title": "Buy milk", "user_id": "{user_id}"}}

### COMMON MISTAKES TO AVOID:
❌ WRONG: ": {{"user_id": "{user_id}"}}"  ← Leading colon!
❌ WRONG: {{user_id: "{user_id}"}}  ← Missing quotes around key!
❌ WRONG: {{"user_id": {user_id}}}  ← Missing quotes around value!

✅ CORRECT: {{"user_id": "{user_id}"}}  ← Clean JSON!

## TOOL USAGE:

### For LISTING tasks:
- User: "What tasks do I have?" → list_tasks with {{"user_id": "{user_id}"}}
- User: "Show pending tasks" → list_tasks with {{"status": "pending", "user_id": "{user_id}"}}

### For CREATING tasks:
- User: "Add a task to buy milk" → add_task with {{"title": "Buy milk", "user_id": "{user_id}"}}

### For COMPLETING tasks:
- User: "Complete task [title]" → FIRST list_tasks, then complete_task with ACTUAL task_id

### For DELETING tasks:
- User: "Delete the go to uni task" → FIRST list_tasks, then delete_task with ACTUAL task_id

## RESPONSE STYLE:
- Use emojis: ✅ Task created, ✅ Task completed, 🗑️ Task deleted
- Use ONLY the tool's message field as your response
- If a tool returns an error, explain it clearly

Remember: Output CLEAN JSON for tool arguments - no extra characters!
user_id is always: "{user_id}"
""",
            model=LitellmModel(
                #  model="gemini/gemini-2.5-flash",
                # api_key=settings.GEMINI_API_KEY
                model="openrouter/qwen/qwen3-coder",
                api_key=settings.OPENROUTER_API_KEY,
            ),
            model_settings=ModelSettings(
                include_usage=True,
                temperature=0.5,  # Lower temperature for more focused responses
                max_tokens=1024, 
                tool_choice="required"  # Reduced tokens for shorter responses
            ),
            mcp_servers=[mcp_server],
        )

        logger.info("Agent created with MCP server: %s", settings.MCP_SERVER_URL)
        return agent, mcp_server

    async def maybe_update_thread_title(
        self,
        thread: ThreadMetadata,
        input_item: UserMessageItem,
        context: Any,
    ) -> None:
        """Generate a title for new threads based on the first user message.

        Args:
            thread: Thread metadata
            input_item: User's message item
            context: Request context
        """
        # Only generate title if thread doesn't have one
        if thread.title is not None:
            logger.debug(f"Thread {thread.id} already has title: '{thread.title}'")
            return

        try:
            logger.info(f"Generating title for thread {thread.id}")

            # Convert user message to agent input
            agent_input = await simple_to_agent_input(input_item)
            logger.debug(f"Agent input: {agent_input}")

            # Run title generation agent
            run = await Runner.run(title_agent, input=agent_input)
            logger.debug(f"Title agent run completed: {run}")

            # Update thread with generated title
            thread.title = run.final_output.strip()
            logger.info(f"Generated title: '{thread.title}'")

            # Save the updated thread
            await self.store.save_thread(thread, context)
            logger.info(
                f"Saved thread with title: '{thread.title}' for thread {thread.id}"
            )

        except Exception as e:
            logger.error(f"Failed to generate thread title: {e}", exc_info=True)
            # Don't fail the request if title generation fails
            # Don't set a fallback title - let it remain None so UI shows date/time

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallItem | None,
        context: Any,
    ) -> AsyncIterator:
        """Handle ChatKit requests and stream responses.

        This method is called by ChatKit for each user message.
        We delegate to our agent orchestration system.

        Args:
            thread: Thread metadata with conversation context
            input: User's input message or tool call
            context: Request context (contains user_id)

        Yields:
            ChatKit-compatible event stream
        """
        try:
            logger.info(
                f"Respond called: thread_id={thread.id}, thread_title={thread.title}, "
                f"input_type={type(input).__name__}, has_input={input is not None}"
            )

            # Generate thread title asynchronously (non-blocking)
            # This runs in the background while the agent responds
            if input and isinstance(input, UserMessageItem):
                import asyncio

                asyncio.create_task(
                    self.maybe_update_thread_title(thread, input, context)
                )

            # Create agent context - gives the agent access to the store
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            # Convert ONLY the new input item to agent format
            new_items = await simple_to_agent_input(input) if input else []

            # Extract user_id from context
            user_id = context.get("user_id", "anonymous")
            logger.info(f"Creating agent for user_id: {user_id}")

            # Create agent with MCP server, passing user_id
            logger.info(f"Creating agent with MCP for user: {user_id}")
            agent, mcp_server = await self._create_agent_with_mcp(user_id)
            logger.info(f"Agent created successfully: {agent.name}")

            # Load full conversation history from the store for context
            try:
                # load_thread_items returns a Page object, access .data for the items list
                thread_items_page = await self.store.load_thread_items(
                    thread_id=thread.id,
                    after=None,  # Load from beginning
                    limit=100,   # Load up to 100 items
                    order='asc', # Oldest first for proper conversation order
                    context=context
                )
                # Convert previous items to agent input format
                history_items = []
                for item in thread_items_page.data:
                    if hasattr(item, 'type'):
                        # Convert each item to the format expected by the agent
                        item_input = await simple_to_agent_input(item)
                        if item_input:
                            history_items.extend(item_input)
                logger.info(f"Loaded {len(history_items)} history items from conversation")
            except Exception as history_err:
                logger.warning(f"Could not load conversation history: {history_err}")
                history_items = []

            # Combine history with new input for full context
            full_input = history_items + new_items
            logger.info(f"Running agent with {len(full_input)} total items ({len(history_items)} history + {len(new_items)} new)")

            # Run the agent with full conversation history
            result = Runner.run_streamed(
                agent,
                full_input,
                context=agent_context,
            )
            logger.info("Agent runner started, beginning to stream events")

            # Stream agent response - manually save assistant messages with unique IDs
            event_count = 0
            saved_message_ids = set()  # Track which messages we've already saved
            seen_message_content = set()  # Track message content to prevent duplicates from retries
            last_content_fingerprint = None  # Track last message fingerprint for near-duplicate detection

            # Patterns that indicate tool response messages (these will be filtered out)
            # Tool responses typically start with emojis like ✅, 🗑️, ✏️ and follow a format
            tool_response_patterns = [
                "✅ task",
                "🗑️ task",
                "✏️ task",
                "🔄 task",
                "📋 task",
            ]

            def is_tool_response(content: str) -> bool:
                """Check if content is a tool response message that should be filtered out."""
                content_lower = content.lower().strip()
                # Check if it starts with any tool response pattern
                for pattern in tool_response_patterns:
                    if content_lower.startswith(pattern):
                        return True
                # Also filter messages that are ONLY tool responses (short, emoji + task + action)
                # Pattern: "emoji Task 'name' action"
                import re
                if re.match(r"^[✅🗑️✏️🔄📋]\s*\w+.*(created|deleted|updated|completed|restored|toggled|moved)$", content):
                    return True
                return False

            def get_content_fingerprint(content: str) -> str:
                """Create a normalized fingerprint for duplicate detection."""
                # Normalize: lowercase, remove extra whitespace, take first 300 chars
                normalized = " ".join(content.lower().split())[:300]
                return normalized

            def is_near_duplicate(content: str, prev_fingerprint: str | None) -> bool:
                """Check if content is identical or nearly identical to previous message."""
                if not prev_fingerprint:
                    return False
                curr_fingerprint = get_content_fingerprint(content)
                # Exact match
                if curr_fingerprint == prev_fingerprint:
                    return True
                # Very similar (one contains the other with minor differences)
                if len(curr_fingerprint) > 50 and len(prev_fingerprint) > 50:
                    # Check if one is a subset of the other (for task lists)
                    if curr_fingerprint in prev_fingerprint or prev_fingerprint in curr_fingerprint:
                        return True
                return False

            logger.info("🔥 Streaming agent response")

            async for event in stream_agent_response(agent_context, result):
                event_count += 1

                # Skip duplicate assistant messages (prevents issues from ChatKit retries)
                if hasattr(event, "item") and hasattr(event, "type") and event.type == "thread.item.done":
                    if event.item.type == "assistant_message":
                        # Extract content for deduplication
                        content = ""
                        if hasattr(event.item, "content") and event.item.content:
                            # Handle different content formats
                            if isinstance(event.item.content, list):
                                content = "".join(
                                    c.get("text", "") if isinstance(c, dict) else str(c)
                                    for c in event.item.content
                                )
                            elif isinstance(event.item.content, dict):
                                content = event.item.content.get("text", "")
                            else:
                                content = str(event.item.content)

                        # Filter out tool response messages (show only agent conversational responses)
                        if content.strip() and is_tool_response(content):
                            logger.info(f"⏭️ Filtering out tool response: {content[:50]}...")
                            # Still track it to avoid duplicate processing
                            content_hash = content.strip()[:100]
                            seen_message_content.add(content_hash)
                            # Skip yielding this event to the user
                            continue

                        # Check for near-duplicate content (same message appearing twice)
                        if is_near_duplicate(content, last_content_fingerprint):
                            logger.info(f"⏭️ Skipping near-duplicate message: {content[:50]}...")
                            content_hash = content.strip()[:100]
                            seen_message_content.add(content_hash)
                            continue

                        # Update fingerprint after processing
                        last_content_fingerprint = get_content_fingerprint(content)

                        content_hash = content.strip()[:100]  # Use first 100 chars as hash
                        if content_hash in seen_message_content:
                            logger.warning(f"⏭️ Skipping duplicate message: {content_hash[:30]}...")
                            continue
                        seen_message_content.add(content_hash)

                # Save assistant message on thread.item.done event (only once per ID)
                if hasattr(event, "item") and hasattr(event, "type") and event.type == "thread.item.done":
                    if event.item.type == "assistant_message":
                        try:
                            # CRITICAL FIX: ChatKit uses __fake_id__ during streaming
                            # Generate a real unique ID before saving
                            if event.item.id == "__fake_id__":
                                real_id = self.store.generate_item_id("message", thread, context)
                                event.item.id = real_id

                            # Only save if we haven't saved this message yet
                            if event.item.id not in saved_message_ids:
                                await self.store.add_thread_item(thread.id, event.item, context)
                                saved_message_ids.add(event.item.id)
                                logger.info(f"✅ Saved assistant message {event.item.id}")
                            else:
                                logger.debug(f"⏭️ Skipping duplicate save for {event.item.id}")

                        except Exception as save_err:
                            logger.error(f"❌ Failed to save assistant message: {save_err}")

                yield event

            logger.info(f"🏁 Streaming complete - Saved {len(saved_message_ids)} unique assistant messages")

            # Trigger frontend revalidation after streaming completes
            # This ensures the UI updates with any task changes made by the chatbot
            await trigger_frontend_revalidation("chatbot_task_change")

        except Exception as e:
            logger.error(f"Error in respond: {e}", exc_info=True)
            # Yield error event in ChatKit format using proper Pydantic model
            yield ErrorEvent(
                type="error",
                code="custom",
                message=f"Failed to process request: {str(e)}",
                allow_retry=True,
            )
