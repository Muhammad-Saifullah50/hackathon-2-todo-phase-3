"""ChatKit endpoint for task management chatbot.

This module provides the single endpoint that ChatKit frontend connects to.
It handles both authenticated and anonymous users.
"""

import os
from typing import Optional

from chatkit.server import StreamingResult
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse

from src.auth import get_current_user
from src.core.chatkit_server import TodoMoreChatKitServer
from src.core.logging import get_logger
from src.models.user import User

logger = get_logger(__name__)
router = APIRouter(tags=["chatkit"])

# Initialize ChatKit server (singleton)
_chatkit_server: Optional[TodoMoreChatKitServer] = None


def get_chatkit_server() -> TodoMoreChatKitServer:
    """Get or create the ChatKit server instance.

    Returns:
        TodoMoreChatKitServer instance
    """
    global _chatkit_server
    if _chatkit_server is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        _chatkit_server = TodoMoreChatKitServer(database_url)
    return _chatkit_server


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """ChatKit integration endpoint.

    This is the single endpoint that ChatKit frontend connects to.
    It receives all requests and returns either JSON or SSE streams.

    The endpoint supports:
    - Session creation/retrieval
    - Message sending with streaming responses
    - Thread history loading
    - Tool invocations through the agent

    Args:
        request: FastAPI request with ChatKit payload
        current_user: Authenticated user from JWT token

    Returns:
        StreamingResponse for SSE or Response for JSON
    """
    try:
        # Extract user ID from authenticated user
        user_id = current_user.id
        if not user_id:
            logger.error("User not authenticated")
            return Response(
                content='{"error": "User not authenticated"}',
                media_type="application/json",
                status_code=401,
            )

        logger.info(
            f"ChatKit request received",
            extra={"user_id": user_id},
        )

        # Read request body early to catch client disconnects
        try:
            body = await request.body()
        except Exception as read_error:
            logger.warning(f"Failed to read request body (client may have disconnected): {read_error}")
            return Response(
                content='{"error": "Client disconnected"}',
                media_type="application/json",
                status_code=499,  # Client Closed Request
            )

        # Extract authorization header for MCP tool calls
        authorization_header = request.headers.get("authorization", "")

        # Build context with user_id and authorization for authenticated users
        context = {
            "user_id": user_id,
            "authorization": authorization_header,  # Pass JWT token for MCP tools
        }

        # Get ChatKit server instance
        server = get_chatkit_server()

        # Process the request using the ChatKit server
        result = await server.process(body, context)
        logger.info(f"ChatKit processing complete, result type: {type(result).__name__}")

        # Return appropriate response type
        if isinstance(result, StreamingResult):
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # Return JSON response (for session creation, etc.)
            return Response(
                content=result.json,
                media_type="application/json",
            )

    except Exception as e:
        logger.error(f"Error in chatkit endpoint: {e}", exc_info=True)
        return Response(
            content=f'{{"error": "{str(e)}"}}',
            media_type="application/json",
            status_code=500,
        )
