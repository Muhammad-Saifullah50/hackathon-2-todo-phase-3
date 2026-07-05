"""ChatKit Server implementation for TodoMore task management.

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
    ThoughtTask,
    UserMessageItem,
    UserMessageTextContent,
    UserMessageTagContent,
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
    json_pattern = r"\{[^{}]*\}"
    matches = list(re.finditer(json_pattern, text))

    if not matches:
        return text

    # Process each JSON-like block
    result = text
    for match in reversed(matches):
        original = match.group()
        sanitized = _sanitize_json_block(original)
        if sanitized != original:
            result = result[: match.start()] + sanitized + result[match.end() :]

    return result


def _sanitize_json_block(block: str) -> str:
    """Sanitize a single JSON block."""
    import re

    # Remove leading/trailing whitespace
    block = block.strip()

    # Remove leading colon if present (common Nebius error)
    block = re.sub(r"^:\s*", "", block)

    # Remove trailing colon if present
    block = re.sub(r":\s*$", "", block)

    # Ensure it starts with { and ends with }
    if not block.startswith("{"):
        # Try to find JSON start
        json_start = block.find("{")
        if json_start != -1:
            block = block[json_start:]
    if not block.endswith("}"):
        # Try to find JSON end
        json_end = block.rfind("}")
        if json_end != -1:
            block = block[: json_end + 1]

    # If still not valid JSON, return original
    if not (block.startswith("{") and block.endswith("}")):
        return block

    # Fix: add quotes around unquoted keys (e.g., {user_id: "..."} -> {"user_id": "..."})
    block = re.sub(r"\{(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):", r'{\1"\2"\3:', block)

    # Fix: add quotes around unquoted string values that are simple words
    # This is trickier - we need to avoid matching numbers, booleans, null
    # Match: key followed by unquoted word (not true/false/null/number)
    def fix_unquoted_value(match):
        before = match.group(1)
        value = match.group(2)
        after = match.group(3)
        # Don't quote if it looks like a number or boolean
        if value.lower() in ("true", "false", "null") or re.match(r"^-?\d+(\.\d+)?$", value):
            return match.group(0)
        return f'{before}"{value}"{after}'

    # Only apply if the value isn't already quoted
    # Match colon followed by word character not preceded by quote
    block = re.sub(r"(:\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])", fix_unquoted_value, block)

    return block


async def trigger_frontend_revalidation(action: str = "update") -> None:
    """Trigger on-demand revalidation on the Next.js frontend.

    This function calls the Next.js API route to invalidate the task cache
    after the chatbot makes changes to tasks.

    Args:
        action: The action that triggered revalidation (create, update, delete, etc.)

    Note:
        This is a best-effort operation. If it fails, we log the error but don't block the response.
    """
    logger.info(f"🔔 Triggering frontend revalidation for action: {action}")
    # Note: The actual revalidation happens via SSE stream events that the frontend listens to
    # This function is kept for compatibility but the real revalidation trigger is the
    # ThreadItemDoneEvent being sent to the frontend


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
        model="openrouter/google/gemma-4-31b-it:free",
        api_key=settings.OPENROUTER_API_KEY,
    ),
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=50,
    ),
)


class TodoMoreChatKitServer(ChatKitServer):
    """ChatKit server implementation for TodoMore task management.

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

    async def _check_mcp_health(self) -> bool:
        """Check if MCP server is healthy and accessible.

        Returns:
            True if MCP server is accessible, False otherwise
        """
        import httpx
        import asyncio

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with asyncio.timeout(5):  # 5 second total timeout
                    # Use root URL for health check, not the MCP endpoint URL
                    health_url = f"{settings.MCP_SERVER_ROOT_URL}/health"
                    logger.info(f"Checking MCP health at: {health_url}")
                    response = await client.get(health_url)
                    if response.status_code == 200:
                        logger.info("✅ MCP server health check passed")
                        return True
                    else:
                        logger.warning(f"⚠️ MCP server health check failed: {response.status_code}")
                        return False
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            logger.warning(f"⚠️ MCP server health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during MCP health check: {e}")
            return False

    async def _create_agent_without_mcp(self, user_id: str) -> Agent:
        """Create agent without MCP tools as fallback.

        Args:
            user_id: Authenticated user ID

        Returns:
            Agent instance without MCP tools
        """
        logger.warning("⚠️ Creating agent WITHOUT MCP tools (degraded mode)")

        agent = Agent(
            name="TodoBot",
            instructions=f"""You are TodoBot, a friendly task management assistant.

            ⚠️ IMPORTANT: You are currently in degraded mode and cannot access task management tools.
            Please inform the user that the task management system is temporarily unavailable and ask them to try again in a moment.

            Be apologetic and friendly. Suggest they:
            1. Try refreshing the page
            2. Wait a moment and try again
            3. Contact support if the issue persists

            user_id: {user_id}
            """,
            model=LitellmModel(
                model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                api_key=settings.OPENROUTER_API_KEY,
            ),
            model_settings=ModelSettings(
                temperature=0.7,
                max_tokens=512,
            ),
        )

        return agent

    async def _create_agent_with_mcp(
        self, user_id: str, authorization: str = ""
    ) -> tuple[Agent, Any]:
        """Create and configure the agent with FastMCP server.

        Args:
            user_id: Authenticated user ID to pass to MCP tools
            authorization: Bearer token for MCP tool authentication

        Returns:
            Tuple of (Agent instance, MCP server instance)

        Raises:
            Exception: If MCP server connection fails
        """
        import httpx
        import asyncio
        from datetime import datetime, timedelta, timezone

        # Create MCP server connection with error handling
        try:
            # Important: Don't cache tools list for serverless environments
            # Each request should be stateless
            mcp_server = MCPServerStreamableHttp(
                name="Task Management Server",
                params={
                    "url": settings.MCP_SERVER_URL,
                    "headers": {
                        "Authorization": f"Bearer {settings.MCP_SERVER_TOKEN}",  # Server-to-server auth
                        "X-User-Authorization": authorization,  # User's JWT token for tool authentication
                        "Content-Type": "application/json",
                        "Accept": "application/json",  # Required by MCP server
                    },
                    "timeout": 30,
                    "sse_read_timeout": 300,  # 5 minutes for long-running operations
                    "terminate_on_close": False,  # CRITICAL: Don't terminate session on close
                },
                cache_tools_list=False,  # Don't cache in serverless
                max_retry_attempts=2,
                client_session_timeout_seconds=60,  # Increase client session timeout
            )

            # Connect to MCP server with timeout
            # Use shorter timeout for faster fallback to degraded mode
            async with asyncio.timeout(5):  # 5 second timeout
                await mcp_server.connect()
                logger.info("✅ Connected to MCP server: %s", settings.MCP_SERVER_URL)

        except asyncio.TimeoutError:
            logger.error("❌ MCP server connection timeout after 5s")
            raise Exception(f"MCP server at {settings.MCP_SERVER_URL} connection timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ MCP server HTTP error: {e.response.status_code} - {e}")
            raise Exception(f"MCP server returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            raise

        # Calculate current date and tomorrow for agent instructions
        now_utc = datetime.now(timezone.utc)
        today_str = now_utc.strftime("%Y-%m-%d")
        tomorrow_str = (now_utc + timedelta(days=1)).strftime("%Y-%m-%d")

        # Create task management agent with MCP server
        agent = Agent(
            name="TodoBot",
            instructions=f"""You are TodoBot, a friendly and helpful task management assistant. You help users manage their tasks through natural, conversational dialogue.

## CRITICAL RULES:
1. You MUST use MCP tools for ALL task operations - NEVER fabricate task IDs or responses
2. ALWAYS pass user_id="{user_id}" to EVERY tool call
3. Use COMPLETE task IDs from tool results - NEVER guess or use partial IDs
4. Wait for tool responses before providing your final confirmation to the user.
5. DO NOT provide a "pre-confirmation" (e.g., "I'll do that now...") before calling the tool. Simply call the tool, then report the result naturally.

## TOOL CALL ARGUMENTS - MUST BE CLEAN JSON:
When providing tool arguments, output ONLY valid JSON.

### EXAMPLES:
✅ CORRECT: {{"user_id": "{user_id}", "status": "pending"}}
✅ CORRECT: {{"title": "Buy milk", "user_id": "{user_id}"}}

❌ WRONG: ": {{"user_id": "{user_id}"}}"  ← Leading colon!
❌ WRONG: {{user_id: "{user_id}"}}  ← Missing quotes around key!
❌ WRONG: {{"title": Buy milk}}  ← Missing quotes around value!

## CONVERSATIONAL RESPONSE STYLE:

After receiving the tool output, provide a single, friendly response:

### For LISTING tasks:
- User: "What tasks do I have?"
- You: "You have 1 pending task: 'Go to university' 📝"

### For CREATING tasks:
- User: "Add a task to buy milk"
- You: "✅ Got it! I've added 'Buy milk' to your task list."

### For COMPLETING tasks:
- User: "Complete the university task"
- You: "✅ Nice work! I've marked 'Go to university' as completed."

### For DELETING tasks:
- User: "Delete the milk task"
- You: "🗑️ Done! I've removed 'Buy milk' from your tasks."

### For EMPTY lists:
- User: "Show my tasks"
- You: "You're all caught up! You don't have any pending tasks right now. 🎉"

## TONE:
- Be friendly and encouraging
- Use emojis appropriately (✅ 📝 🗑️ ✏️ 🎉)
- Keep responses concise but warm
- Celebrate completions with positive reinforcement

## TOOL USAGE PATTERNS:

1. **Listing tasks**: Call list_tasks with {{"user_id": "{user_id}"}} or {{"user_id": "{user_id}", "status": "pending"}}

2. **Creating tasks**: Call add_task with {{"title": "Task name", "user_id": "{user_id}"}}
   - For due dates, you MUST convert relative dates to ISO format YYYY-MM-DD
   - TODAY is: {today_str}
   - TOMORROW is: {tomorrow_str}
   - CRITICAL CONVERSION EXAMPLES:
     * User says "tomorrow" → you use "{tomorrow_str}"
     * User says "today" → you use "{today_str}"
     * User says "next Monday" → calculate and use exact date like "2026-01-10"
     * User says "Friday" → if today is {today_str}, calculate which Friday (this week or next)
     * User says "in 3 days" → add 3 days to {today_str}
   - ALWAYS pass the ISO date string (YYYY-MM-DD format) in the due_date parameter
   - DO NOT pass "tomorrow" or "today" as strings - ALWAYS convert to actual dates

3. **Completing tasks**: FIRST call list_tasks to find the task, THEN call complete_task with {{"task_id": "actual_id", "user_id": "{user_id}"}}

4. **Deleting tasks**: FIRST call list_tasks to find the task, THEN call delete_task with {{"task_id": "actual_id", "user_id": "{user_id}"}}

Remember: Always use clean JSON for arguments, and respond naturally like a helpful friend!
Your user_id is always: "{user_id}"
""",
            model=LitellmModel(
                model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                api_key=settings.OPENROUTER_API_KEY,
            ),
            model_settings=ModelSettings(
                include_usage=True,
                temperature=0.5,  # Slightly higher for more natural, conversational responses
                max_tokens=1024,
                tool_choice="auto",  # Allow agent to decide when to use tools vs respond naturally
            ),
            mcp_servers=[mcp_server],
        )

        logger.info("Agent created with MCP server: %s", settings.MCP_SERVER_URL)
        return agent, mcp_server

    def _looks_like_instructions(self, output: str, user_text: str) -> bool:
        """Check if the generated title is LLM reasoning rather than an actual title."""
        instruction_phrases = [
            "you generate",
            "create a short title",
            "return only",
            "3-6 words",
            "based on the user",
            "need to output",
            "your task is",
            "generate a concise",
        ]
        output_lower = output.lower()
        for phrase in instruction_phrases:
            if phrase in output_lower:
                return True
        # Check if output contains the user's message (model echoing it back)
        user_words = set(user_text.lower().split())
        if len(user_words) > 2:
            matches = sum(1 for w in user_words if w in output_lower and len(w) > 2)
            if matches >= 3:
                return True
        return False

    def _extract_user_title(self, input_item: UserMessageItem) -> str:
        """Extract a short title from the user's message text."""
        text_parts = []
        for part in input_item.content:
            if isinstance(part, UserMessageTextContent):
                text_parts.append(part.text)
            elif isinstance(part, UserMessageTagContent):
                text_parts.append(part.text)
        words = " ".join(text_parts).split()
        return " ".join(words[:6])

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
            raw_title = run.final_output.strip()
            user_text = self._extract_user_title(input_item)

            # If model returned empty string, fall back to user text
            if not raw_title:
                logger.warning("Title agent returned empty string, falling back to user text")
                thread.title = user_text
            elif self._looks_like_instructions(raw_title, user_text):
                logger.warning(
                    f"Title agent returned instructions instead of title, falling back to user text"
                )
                thread.title = user_text
            else:
                # Truncate long titles
                MAX_TITLE_LENGTH = 100
                if len(raw_title) > MAX_TITLE_LENGTH:
                    thread.title = raw_title[:MAX_TITLE_LENGTH].rsplit(" ", 1)[0] + "..."
                    logger.warning(
                        f"Truncated title from {len(raw_title)} to {len(thread.title)} chars"
                    )
                else:
                    thread.title = raw_title
            logger.info(f"Generated title: '{thread.title}'")

            # Save the updated thread
            await self.store.save_thread(thread, context)
            logger.info(f"Saved thread with title: '{thread.title}' for thread {thread.id}")

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
        # Store MCP server reference to ensure proper cleanup
        mcp_server = None

        try:
            logger.info(
                f"Respond called: thread_id={thread.id}, thread_title={thread.title}, "
                f"input_type={type(input).__name__}, has_input={input is not None}"
            )

            # Generate thread title synchronously before streaming begins
            # This ensures the title is set before _process_events captures last_thread,
            # preventing a mid-stream ThreadUpdatedEvent that could confuse ChatKit
            if input and isinstance(input, UserMessageItem):
                await self.maybe_update_thread_title(thread, input, context)

            # Create agent context - gives the agent access to the store
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            # Convert ONLY the new input item to agent format
            new_items = await simple_to_agent_input(input) if input else []

            # Extract user_id and authorization from context
            user_id = context.get("user_id", "anonymous")
            authorization = context.get("authorization", "")
            logger.info(f"Creating agent for user_id: {user_id}")

            # Try to create agent with MCP server, with fallback to degraded mode
            logger.info(f"Creating agent with MCP for user: {user_id}")

            # First, check if MCP server is healthy (quick health check)
            mcp_healthy = await self._check_mcp_health()

            if not mcp_healthy:
                logger.warning("⚠️ MCP server health check failed, using degraded mode")
                agent = await self._create_agent_without_mcp(user_id)
                mcp_server = None
                logger.info(f"⚠️ Agent created in degraded mode (no health): {agent.name}")
            else:
                # Health check passed, try to connect
                try:
                    agent, mcp_server = await self._create_agent_with_mcp(user_id, authorization)
                    logger.info(f"✅ Agent created successfully with MCP tools: {agent.name}")
                except Exception as mcp_error:
                    logger.error(f"❌ Failed to create agent with MCP: {mcp_error}")
                    logger.info("🔄 Falling back to degraded mode (connection failed)")

                    # Fallback: create agent without MCP tools
                    agent = await self._create_agent_without_mcp(user_id)
                    mcp_server = None  # No MCP server in degraded mode
                    logger.info(f"⚠️ Agent created in degraded mode (fallback): {agent.name}")

            # Load full conversation history from the store for context
            try:
                # load_thread_items returns a Page object, access .data for the items list
                thread_items_page = await self.store.load_thread_items(
                    thread_id=thread.id,
                    after=None,  # Load from beginning
                    limit=100,  # Load up to 100 items
                    order="asc",  # Oldest first for proper conversation order
                    context=context,
                )
                # Convert previous items to agent input format
                history_items = []
                for item in thread_items_page.data:
                    if hasattr(item, "type"):
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
            logger.info(
                f"Running agent with {len(full_input)} total items ({len(history_items)} history + {len(new_items)} new)"
            )

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

            # SESSION DEDUPLICATION: Track messages sent in this specific response stream
            sent_message_ids = set()  # Track by message ID
            sent_message_content = set()  # Track by message content to catch duplicates

            logger.info("🔥 Streaming agent response")

            # Track if we've triggered revalidation (only once per request)
            has_revalidated = False

            async for event in stream_agent_response(agent_context, result):
                event_count += 1
                raw_type = getattr(event, "type", "unknown")
                logger.debug(f"📩 Received event #{event_count} from agent: type={raw_type}")

                # Trigger revalidation immediately after any item is added to the thread
                if (
                    not has_revalidated
                    and hasattr(event, "type")
                    and event.type == "thread.item.added"
                ):
                    import asyncio

                    asyncio.create_task(trigger_frontend_revalidation("chatbot_tool_call"))
                    has_revalidated = True
                    logger.info("⚡ Triggered fast revalidation after item added")

                # Skip streaming updates (thread.item.updated) for assistant messages
                # Only show final complete message (thread.item.done)
                # Note: ThreadItemUpdatedEvent has item_id + update, NOT an .item field
                if (
                    hasattr(event, "type")
                    and event.type == "thread.item.updated"
                    and hasattr(event, "update")
                    and hasattr(event.update, "type")
                    and isinstance(event.update.type, str)
                    and event.update.type.startswith("assistant_message.")
                ):
                    logger.debug(
                        f"⏭️ Skipping streaming update for assistant message: {event.update.type}"
                    )
                    continue  # Don't yield streaming deltas

                # Skip workflow task updates - we'll show a single "Thinking..." step instead
                if (
                    hasattr(event, "type")
                    and event.type == "thread.item.updated"
                    and hasattr(event, "update")
                    and hasattr(event.update, "type")
                    and isinstance(event.update.type, str)
                    and event.update.type.startswith("workflow.")
                ):
                    logger.debug(f"⏭️ Skipping workflow task update: {event.update.type}")
                    continue  # Don't yield task-level progress

                # DEDUPLICATION LOGIC: Only process and yield final complete messages
                if (
                    hasattr(event, "item")
                    and hasattr(event, "type")
                    and event.type == "thread.item.done"
                    and event.item.type == "assistant_message"
                ):
                    # Extract text content for logging and deduplication
                    content = ""
                    if hasattr(event.item, "content") and event.item.content:
                        if isinstance(event.item.content, list):
                            parts = []
                            for c in event.item.content:
                                if isinstance(c, dict):
                                    parts.append(c.get("text", ""))
                                elif hasattr(c, "text"):
                                    parts.append(c.text)
                                else:
                                    parts.append(str(c))
                            content = "".join(parts)
                        elif isinstance(event.item.content, dict):
                            content = event.item.content.get("text", "")
                        else:
                            content = str(event.item.content)

                    if not content.strip():
                        logger.info("⏭️ Skipping empty message")
                        continue  # Don't yield empty messages

                    # Normalize content for comparison (remove extra whitespace)
                    normalized_content = " ".join(content.split())

                    # Check if we've already sent this exact message content
                    if normalized_content in sent_message_content:
                        logger.warning(
                            f"🚫 BLOCKED DUPLICATE MESSAGE CONTENT: {normalized_content[:100]}..."
                        )
                        continue  # Don't yield duplicate content

                    # Check if we've already sent this message ID
                    if event.item.id in sent_message_ids:
                        logger.warning(f"🚫 BLOCKED DUPLICATE MESSAGE ID: {event.item.id}")
                        continue  # Don't yield duplicates

                    # Regenerate placeholder IDs to prevent collisions
                    if event.item.id == "__fake_id__" or "__fake_id__" in str(event.item.id):
                        event.item.id = self.store.generate_item_id("message", thread, context)
                        logger.info(f"✨ Generated real ID for fake message: {event.item.id}")

                    # Record this message ID and content as sent
                    sent_message_ids.add(event.item.id)
                    sent_message_content.add(normalized_content)
                    logger.info(f"📤 Agent message ({event.item.id}): {content[:100]}...")

                    # Save to database if needed
                    try:
                        if event.item.id not in saved_message_ids:
                            await self.store.add_thread_item(thread.id, event.item, context)
                            saved_message_ids.add(event.item.id)
                    except Exception as save_err:
                        logger.error(f"❌ Failed to save assistant message: {save_err}")

                    # CRITICAL: Only yield the final complete event
                    yield event

                    # AFTER yielding the message, trigger revalidation
                    logger.info("🔔 Assistant message sent - frontend should revalidate now")
                elif (
                    hasattr(event, "type")
                    and event.type == "thread.item.added"
                    and hasattr(event, "item")
                    and hasattr(event.item, "type")
                    and event.item.type == "workflow"
                ):
                    # Pre-populate workflow with a "Thinking..." task so ChatKit
                    # shows it immediately instead of the default "Thought for a moment"
                    if not event.item.workflow.tasks or len(event.item.workflow.tasks) == 0:
                        event.item.workflow.tasks = [
                            ThoughtTask(
                                title="Thinking...",
                                content="Processing your request",
                            )
                        ]
                    event_id = getattr(event.item, "id", "unknown")
                    logger.debug(f"📡 Yielding workflow added with Thinking task: id={event_id}")
                    yield event
                elif (
                    hasattr(event, "type")
                    and event.type == "thread.item.done"
                    and hasattr(event, "item")
                    and hasattr(event.item, "type")
                    and event.item.type == "workflow"
                ):
                    # Simplify workflow tasks to a single clean "Thinking..." step
                    event.item.workflow.tasks = [
                        ThoughtTask(
                            title="Thinking...",
                            content="Processing your request",
                        )
                    ]
                    event_id = getattr(event.item, "id", "unknown")
                    logger.debug(f"📡 Yielding simplified workflow done: id={event_id}")
                    yield event
                else:
                    event_type = getattr(event, "type", "unknown")
                    event_id = getattr(event, "item_id", getattr(event, "id", "unknown"))
                    if hasattr(event, "item"):
                        event_id = getattr(event.item, "id", event_id)
                    logger.debug(f"📡 Yielding event: type={event_type}, id={event_id}")
                    # For non-assistant-message events (tool calls, etc.), yield normally
                    yield event

            logger.info(
                f"🏁 Streaming complete - Saved {len(saved_message_ids)} unique assistant messages"
            )

            # Fallback: trigger revalidation at end if we didn't do it earlier
            # This handles cases where no tool calls were made
            if not has_revalidated:
                await trigger_frontend_revalidation("chatbot_completion")
                logger.info("⚡ Triggered fallback revalidation at completion")

        except Exception as e:
            logger.error(f"Error in respond: {e}", exc_info=True)
            # Yield error event in ChatKit format using proper Pydantic model
            yield ErrorEvent(
                type="error",
                code="custom",
                message=f"Failed to process request: {str(e)}",
                allow_retry=True,
            )
        finally:
            # Ensure MCP server is properly disconnected in the same task context
            if mcp_server is not None:
                import asyncio

                try:
                    # Use asyncio.shield to ensure cleanup completes even if task is cancelled
                    await asyncio.shield(mcp_server.cleanup())
                    logger.info("✅ MCP server cleaned up successfully")
                except asyncio.CancelledError:
                    # If cleanup is cancelled, log but don't raise
                    logger.warning("⚠️ MCP server cleanup was cancelled")
                except Exception as cleanup_err:
                    logger.warning(f"⚠️ Error cleaning up MCP server: {cleanup_err}")
