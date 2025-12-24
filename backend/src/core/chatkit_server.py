"""ChatKit Server implementation for Todoly task management.

This module provides the ChatKit server that bridges the ChatKit frontend
with our OpenAI Agents SDK + FastMCP + LiteLLM backend.
"""

import os
from typing import Any, AsyncIterator

from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStdio
from agents.extensions.models.litellm_model import LitellmModel
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ClientToolCallItem, ThreadMetadata, UserMessageItem

from src.core.chatkit_store import NeonChatKitStore
from src.core.logging import get_logger

logger = get_logger(__name__)


# Title generation agent - creates concise thread titles from user's first message
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
        model="zai/glm-4.5-air",
        api_key=os.getenv("ZAI_API_KEY"),
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

    async def _create_agent_with_mcp(self) -> tuple[Agent, MCPServerStdio]:
        """Create and configure the agent with FastMCP server.

        Returns:
            Tuple of (Agent instance, MCP server instance)
        """
        # Get ZAI API key from environment
        zai_api_key = os.getenv("ZAI_API_KEY")
        if not zai_api_key:
            logger.warning("ZAI_API_KEY not found in environment")

        # Create MCP server instance for FastMCP
        mcp_server = MCPServerStdio(
            name="Task Management Server",
            params={
                "command": "python",
                "args": ["-m", "src.mcp_server.server"],
            },
        )

        # Create task management agent
        agent = Agent(
            name="TaskBot",
            instructions="""You are a helpful task management assistant. Your role is to help users manage their tasks through natural conversation.

**Your Capabilities:**
- Create new tasks with natural language descriptions using add_task tool
- List and filter tasks by status, priority, or tags using list_tasks tool
- Parse due dates from expressions like "tomorrow", "next Friday", "in 2 weeks"
- Set task priorities (low, medium, high)
- Add tags to organize tasks
- Help users stay organized and productive

**Guidelines:**
- Always be friendly and encouraging
- When creating tasks, extract all relevant details (title, description, due date, priority, tags)
- If a due date is ambiguous, ask clarifying questions
- Confirm actions with clear, concise messages
- Use emojis to make interactions engaging (✅ ✏️ 📝 📋 🎯 etc.)

**Available Tools:**
- add_task(title, description, due_date, priority, tags): Create a new task
- list_tasks(status, priority, tags): List tasks with optional filters

**Example Interactions:**

User: "Add a task to buy groceries tomorrow"
You: *Call add_task(title="Buy groceries", due_date="tomorrow")*
Response: "✅ I've added 'Buy groceries' to your tasks, due tomorrow!"

User: "Show me my pending tasks"
You: *Call list_tasks(status="pending")*
Response: "📋 Here are your pending tasks: [list from tool result]"

User: "Create a high priority task to finish the report by Friday with tags work and urgent"
You: *Call add_task(title="Finish the report", due_date="Friday", priority="high", tags=["work", "urgent"])*
Response: "✅ Created high priority task 'Finish the report', due Friday! Tagged with work, urgent."

**Important:**
- Always use the available tools to perform actions
- Extract task details from natural language
- Be conversational and helpful
- Confirm what you've done with the results from the tools""",
            model=LitellmModel(
                model="zai/glm-4.5-air",
                api_key=zai_api_key,
            ),
            model_settings=ModelSettings(
                include_usage=True,
                temperature=0.7,
                max_tokens=2048,
            ),
            mcp_servers=[mcp_server],
        )

        logger.info("Agent created with GLM-4.5-air model and FastMCP tools")
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
            return

        try:
            # Convert user message to agent input
            agent_input = await simple_to_agent_input(input_item)

            # Run title generation agent
            run = await Runner.run(title_agent, input=agent_input)

            # Update thread with generated title
            thread.title = run.final_output.strip()

            # Save the updated thread
            await self.store.save_thread(thread, context)

            logger.info(
                f"Generated thread title: '{thread.title}' for thread {thread.id}"
            )
        except Exception as e:
            logger.error(f"Failed to generate thread title: {e}", exc_info=True)
            # Don't fail the request if title generation fails

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
            # Generate thread title asynchronously (non-blocking)
            if input and isinstance(input, UserMessageItem):
                # Don't await - let it run in background
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

            # Create agent with MCP server
            agent, mcp_server = await self._create_agent_with_mcp()

            # Run the agent with only the new input
            # The agent will fetch history through AgentContext as needed
            result = Runner.run_streamed(
                agent,
                new_items,
                context=agent_context,
            )

            # Stream agent response - ChatKit handles saving to store automatically
            async for event in stream_agent_response(agent_context, result):
                yield event

        except Exception as e:
            logger.error(f"Error in respond: {e}", exc_info=True)
            # Yield error event in ChatKit format
            yield {
                "type": "error",
                "error": {
                    "message": f"Failed to process request: {str(e)}",
                    "code": "INTERNAL_ERROR",
                },
            }
