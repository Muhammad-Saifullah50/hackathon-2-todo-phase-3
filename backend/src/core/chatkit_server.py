"""ChatKit Server implementation for Todoly task management.

This module provides the ChatKit server that bridges the ChatKit frontend
with our OpenAI Agents SDK + FastMCP + LiteLLM backend.
"""

from typing import Any, AsyncIterator

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
        model="gemini/gemini-2.5-flash-lite",
        api_key=settings.GEMINI_API_KEY,
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

    async def _create_agent_with_mcp(self) -> tuple[Agent | None]:
        """Create and configure the agent with FastMCP server.

        Returns:
            Tuple of (Agent instance, MCP server instance)
        """
        # # Create MCP server instance for FastMCP
        # mcp_server = MCPServerStdio(
        #     name="Task Management Server",
        #     params={
        #         "command": "python",
        #         "args": ["-m", "src.mcp_server.server"],
        #     },
        # )


        # Create task management agent (without MCP for now)
        agent = Agent(
            name="TaskBot",
            instructions="""You are a helpful task management assistant. Your role is to help users manage their tasks through natural conversation.

**Your Capabilities:**
- Answer questions about tasks
- Provide friendly and helpful responses
- Be conversational and engaging

**Guidelines:**
- Always be friendly and encouraging
- Be conversational and helpful
- Use emojis to make interactions engaging (✅ ✏️ 📝 📋 🎯 etc.)

**Important:**
- Be conversational and helpful
- Provide friendly responses to user queries""",
            model=LitellmModel(
                model="gemini/gemini-2.5-flash-lite",
                api_key=settings.GEMINI_API_KEY,
            ),
            model_settings=ModelSettings(
                include_usage=True,
                temperature=0.7,
                max_tokens=2048,
            ),
            # mcp_servers=[mcp_server],  # Commented out for now
        )

        logger.info("Agent created with GLM-4.5-air model (MCP disabled)")
        return agent, None  # Return None for MCP server

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
            # Yield error event in ChatKit format using proper Pydantic model
            yield ErrorEvent(
                type="error",
                code="custom",
                message=f"Failed to process request: {str(e)}",
                allow_retry=True,
            )
