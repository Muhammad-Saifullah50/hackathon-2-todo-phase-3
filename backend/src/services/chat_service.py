"""Chat service for AI agent orchestration with OpenAI Agents SDK + LiteLLM + FastMCP.

This service integrates:
- OpenAI Agents SDK for agent orchestration
- LiteLLM for multi-provider LLM access (GLM-4.5-air)
- FastMCP for task management tool exposure via MCP protocol
"""

import os
from typing import AsyncGenerator
from uuid import UUID

from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStdio
from agents.extensions.models.litellm_model import LitellmModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.models.conversation import ConversationCreate
from src.models.message import MessageCreate
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService

logger = get_logger(__name__)


class ChatService:
    """Service for AI chat interactions with task management capabilities.

    This service orchestrates conversations between users and the AI agent,
    managing conversation history, tool invocations, and response streaming.

    The agent uses:
    - GLM-4.5-air model via LiteLLM for cost-effective AI responses
    - FastMCP server for task management tool exposure
    - OpenAI Agents SDK for orchestration
    """

    def __init__(self, session: AsyncSession, user_id: str):
        """Initialize the ChatService.

        Args:
            session: Async database session.
            user_id: ID of the authenticated user.
        """
        self.session = session
        self.user_id = user_id
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        # Agent will be created per request with MCP server

    async def _create_agent_with_mcp(self) -> tuple[Agent, MCPServerStdio]:
        """Create and configure the OpenAI Agent with FastMCP server.

        The agent is configured with:
        - Task management instructions
        - GLM-4.5-air model via LiteLLM
        - FastMCP server for tool access

        Returns:
            Tuple of (Agent instance, MCP server instance).
        """
        # Get ZAI API key from environment
        zai_api_key = os.getenv("ZAI_API_KEY")
        if not zai_api_key:
            logger.warning("ZAI_API_KEY not found in environment")

        # Create MCP server instance for FastMCP
        # Run FastMCP as a subprocess via stdio transport
        mcp_server = MCPServerStdio(
            name="Task Management Server",
            params={
                "command": "python",
                "args": ["-m", "src.mcp_server.server"],  # Run our FastMCP server
            },
        )

        # Create agent with GLM-4.5-air via LiteLLM
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
                model="zai/glm-4.5-air",  # Zhipu AI's GLM-4.5-air via LiteLLM
                api_key=zai_api_key,
            ),
            model_settings=ModelSettings(
                include_usage=True,
                temperature=0.7,
                max_tokens=2048,
            ),
            mcp_servers=[mcp_server],  # Connect FastMCP server to agent
        )

        logger.info("Agent created with GLM-4.5-air model and FastMCP tools")
        return agent, mcp_server

    async def send_message(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Send a message and stream the AI response.

        This method:
        1. Creates or retrieves a conversation
        2. Saves the user's message
        3. Loads conversation context (last 50 messages)
        4. Creates agent with MCP server connection
        5. Streams the agent's response
        6. Saves the agent's response
        7. Updates conversation timestamp

        Args:
            message: User's message text.
            conversation_id: Optional conversation ID to continue existing conversation.

        Yields:
            Dictionary chunks with streaming response data:
            - {"type": "token", "content": "...", "conversation_id": "..."}
            - {"type": "done", "conversation_id": "...", "message_id": "..."}
            - {"type": "error", "content": "..."}

        Example:
            ```python
            async for chunk in chat_service.send_message("Add a task"):
                if chunk["type"] == "token":
                    print(chunk["content"], end="", flush=True)
            ```
        """
        try:
            # Create or get conversation
            if conversation_id:
                conversation = await self.conversation_service.get_conversation_by_id(
                    conversation_id, self.user_id
                )
                if not conversation:
                    yield {
                        "type": "error",
                        "content": "Conversation not found",
                    }
                    return
            else:
                conversation = await self.conversation_service.create_conversation(
                    ConversationCreate(title=None), self.user_id
                )

            # Save user message
            user_message = await self.message_service.create_message(
                MessageCreate(role="user", content=message),
                conversation.id,
                self.user_id,
            )

            logger.info(
                f"User message saved: {user_message.id}",
                extra={"conversation_id": str(conversation.id)},
            )

            # Load conversation context (last 50 messages)
            context_messages = await self.message_service.get_conversation_context(
                conversation.id, self.user_id, limit=50
            )

            # Build context for agent (exclude the message we just added)
            agent_context = []
            for msg in context_messages[:-1]:
                agent_context.append({"role": msg.role, "content": msg.content})

            logger.info(
                f"Loaded {len(agent_context)} context messages",
                extra={"conversation_id": str(conversation.id)},
            )

            # Create agent with MCP server and stream response
            assistant_content = ""
            async with await self._create_agent_with_mcp() as (agent, mcp_server):
                async for chunk in self._stream_agent_response(agent, message, agent_context):
                    if chunk["type"] == "token":
                        assistant_content += chunk["content"]

                    yield {
                        **chunk,
                        "conversation_id": str(conversation.id),
                    }

            # Save assistant message
            assistant_message = await self.message_service.create_message(
                MessageCreate(role="assistant", content=assistant_content),
                conversation.id,
                self.user_id,
            )

            logger.info(
                f"Assistant message saved: {assistant_message.id}",
                extra={"conversation_id": str(conversation.id)},
            )

            # Update conversation timestamp
            await self.conversation_service.update_conversation_timestamp(
                conversation.id, self.user_id
            )

            # Send completion event
            yield {
                "type": "done",
                "conversation_id": str(conversation.id),
                "message_id": str(assistant_message.id),
            }

        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"AI service temporarily unavailable: {str(e)}",
            }

    async def _stream_agent_response(
        self, agent: Agent, message: str, context: list[dict]
    ) -> AsyncGenerator[dict, None]:
        """Stream response from the OpenAI Agent.

        The agent will automatically invoke FastMCP tools as needed based on the
        user's message and conversation context.

        Args:
            agent: Configured Agent instance with MCP servers.
            message: User's current message.
            context: Previous conversation messages for context.

        Yields:
            Dictionary chunks with token content or error information:
            - {"type": "token", "content": "word "}
            - {"type": "error", "content": "error message"}
        """
        try:
            # Run agent - the Runner will handle tool invocations automatically
            response_text = await Runner.run(
                starting_agent=agent,
                input=message,
                # TODO: Pass conversation context if supported by Runner
            )

            # Extract final output
            final_output = response_text.final_output if hasattr(response_text, 'final_output') else str(response_text)

            # Stream the response word by word
            words = final_output.split()
            for i, word in enumerate(words):
                yield {
                    "type": "token",
                    "content": word + (" " if i < len(words) - 1 else ""),
                }

        except Exception as e:
            logger.error(f"Error streaming agent response: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"Failed to get AI response: {str(e)}",
            }
