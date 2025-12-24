"""Neon PostgreSQL implementation of ChatKit Store interface.

This module provides persistent storage for ChatKit threads and messages
using asyncpg for Neon serverless PostgreSQL.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional
import asyncpg
from pydantic import TypeAdapter

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata


class NeonChatKitStore(Store[Dict[str, Any]]):
    """ChatKit Store implementation using Neon PostgreSQL.

    Provides persistent storage for chat threads and messages with connection pooling
    for serverless database access.
    """

    # TypeAdapter for validating ThreadItem Union types
    _thread_item_adapter = TypeAdapter(ThreadItem)

    def __init__(self, connection_string: str):
        """Initialize the store with Neon database connection string.

        Args:
            connection_string: PostgreSQL connection string for Neon database
        """
        self.connection_string = connection_string
        self._pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool for database operations."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
        return self._pool

    async def close(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    def generate_thread_id(self, context: Dict[str, Any]) -> str:
        """Generate a unique thread identifier."""
        return f"thread_{uuid.uuid4().hex[:16]}"

    def generate_item_id(
        self,
        item_type: Literal["message", "tool_call", "task", "workflow", "attachment"],
        thread: ThreadMetadata,
        context: Dict[str, Any],
    ) -> str:
        """Generate a unique item identifier."""
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    async def load_thread(self, thread_id: str, context: Dict[str, Any]) -> ThreadMetadata:
        """Load thread metadata by ID.

        Args:
            thread_id: Thread identifier
            context: Request context (may contain user_id)

        Returns:
            ThreadMetadata instance

        Raises:
            NotFoundError: If thread doesn't exist
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, title, metadata, created_at, updated_at
                FROM chat_threads
                WHERE id = $1
                """,
                thread_id
            )

            if not row:
                raise NotFoundError(f"Thread {thread_id} not found")

            # Parse JSONB metadata (asyncpg returns it as string)
            metadata = row["metadata"]
            if isinstance(metadata, str):
                metadata = json.loads(metadata) if metadata else {}
            elif metadata is None:
                metadata = {}

            thread = ThreadMetadata(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"],
                metadata=metadata
            )
            return thread

    async def save_thread(self, thread: ThreadMetadata, context: Dict[str, Any]) -> None:
        """Save or update thread metadata.

        Args:
            thread: Thread metadata to save
            context: Request context
        """
        pool = await self.get_pool()
        user_id = context.get("user_id")

        # Extract title from metadata or thread.title attribute
        title = None
        if hasattr(thread, 'title') and thread.title:
            title = thread.title
        elif isinstance(thread.metadata, dict):
            title = thread.metadata.get("title")

        async with pool.acquire() as conn:
            # Upsert: INSERT with ON CONFLICT UPDATE
            await conn.execute(
                """
                INSERT INTO chat_threads (id, user_id, title, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4::jsonb, $5, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                """,
                thread.id,
                user_id,
                title,
                json.dumps(thread.metadata if thread.metadata else {}),
                thread.created_at
            )

    async def load_threads(
        self, limit: int, after: Optional[str], order: str, context: Dict[str, Any]
    ) -> Page[ThreadMetadata]:
        """Load paginated list of threads for the current user.

        Args:
            limit: Maximum threads to return
            after: Cursor for pagination (thread ID)
            order: Sort order ('asc' or 'desc')
            context: Request context containing user_id

        Returns:
            Page of ThreadMetadata
        """
        pool = await self.get_pool()
        user_id = context.get("user_id")

        async with pool.acquire() as conn:
            # Build query based on pagination cursor
            if after:
                cursor_row = await conn.fetchrow(
                    "SELECT created_at FROM chat_threads WHERE id = $1",
                    after
                )
                if not cursor_row:
                    after = None

            # Build WHERE clause - handle NULL user_id for anonymous users
            if user_id is None:
                where_clause = "user_id IS NULL"
                params_base = []
            else:
                where_clause = "user_id = $1"
                params_base = [user_id]

            # Fetch threads with pagination
            if after and cursor_row:
                if order == "desc":
                    query = f"""
                        SELECT id, user_id, title, metadata, created_at, updated_at
                        FROM chat_threads
                        WHERE {where_clause} AND created_at < ${len(params_base) + 1}
                        ORDER BY created_at DESC
                        LIMIT ${len(params_base) + 2}
                    """
                    rows = await conn.fetch(query, *params_base, cursor_row["created_at"], limit + 1)
                else:
                    query = f"""
                        SELECT id, user_id, title, metadata, created_at, updated_at
                        FROM chat_threads
                        WHERE {where_clause} AND created_at > ${len(params_base) + 1}
                        ORDER BY created_at ASC
                        LIMIT ${len(params_base) + 2}
                    """
                    rows = await conn.fetch(query, *params_base, cursor_row["created_at"], limit + 1)
            else:
                query = f"""
                    SELECT id, user_id, title, metadata, created_at, updated_at
                    FROM chat_threads
                    WHERE {where_clause}
                    ORDER BY created_at {'DESC' if order == 'desc' else 'ASC'}
                    LIMIT ${len(params_base) + 1}
                """
                rows = await conn.fetch(query, *params_base, limit + 1)

            # Check if there are more pages
            has_more = len(rows) > limit
            data_rows = rows[:limit]

            # Convert rows to ThreadMetadata objects
            threads = []
            for row in data_rows:
                # Parse JSONB metadata
                metadata = row["metadata"]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata) if metadata else {}
                elif metadata is None:
                    metadata = {}

                threads.append(ThreadMetadata(
                    id=row["id"],
                    title=row["title"],
                    created_at=row["created_at"],
                    metadata=metadata
                ))

            return Page(
                data=threads,
                has_more=has_more,
                after=threads[-1].id if has_more and threads else None
            )

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: Dict[str, Any],
    ) -> Page[ThreadItem]:
        """Load paginated list of items (messages) in a thread.

        Args:
            thread_id: Thread identifier
            after: Cursor for pagination (item ID)
            limit: Maximum items to return
            order: Sort order ('asc' or 'desc')
            context: Request context

        Returns:
            Page of ThreadItem
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            # Build query based on pagination cursor
            if after:
                cursor_row = await conn.fetchrow(
                    "SELECT created_at FROM chat_thread_items WHERE id = $1",
                    after
                )
                if not cursor_row:
                    after = None

            # Fetch items with pagination
            if after and cursor_row:
                if order == "desc":
                    query = """
                        SELECT id, thread_id, type, role, content, created_at, n_tokens
                        FROM chat_thread_items
                        WHERE thread_id = $1 AND created_at < $2
                        ORDER BY created_at DESC
                        LIMIT $3
                    """
                    rows = await conn.fetch(query, thread_id, cursor_row["created_at"], limit + 1)
                else:
                    query = """
                        SELECT id, thread_id, type, role, content, created_at, n_tokens
                        FROM chat_thread_items
                        WHERE thread_id = $1 AND created_at > $2
                        ORDER BY created_at ASC
                        LIMIT $3
                    """
                    rows = await conn.fetch(query, thread_id, cursor_row["created_at"], limit + 1)
            else:
                query = f"""
                    SELECT id, thread_id, type, role, content, created_at, n_tokens
                    FROM chat_thread_items
                    WHERE thread_id = $1
                    ORDER BY created_at {'DESC' if order == 'desc' else 'ASC'}
                    LIMIT $2
                """
                rows = await conn.fetch(query, thread_id, limit + 1)

            # Check if there are more pages
            has_more = len(rows) > limit
            data_rows = rows[:limit]

            # Convert rows to ThreadItem objects
            items = []
            for row in data_rows:
                # Parse JSONB content
                content = row["content"]
                if isinstance(content, str):
                    content = json.loads(content)

                # Build item data with required fields for ChatKit types
                item_data = {
                    "id": row["id"],
                    "thread_id": thread_id,
                    "type": row["type"],
                    "content": content,
                    "created_at": row["created_at"]
                }

                # Add role if present
                if row["role"]:
                    item_data["role"] = row["role"]

                # Add inference_options for message types
                if row["type"] in ("user_message", "assistant_message"):
                    item_data["inference_options"] = {}

                items.append(self._thread_item_adapter.validate_python(item_data))

            return Page(
                data=items,
                has_more=has_more,
                after=items[-1].id if has_more and items else None
            )

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: Dict[str, Any]
    ) -> None:
        """Add a new item to a thread.

        Args:
            thread_id: Thread identifier
            item: Thread item to add
            context: Request context
        """
        pool = await self.get_pool()

        # Convert item to dict using Pydantic's model_dump
        item_dict = item.model_dump(mode='json')
        content_dict = item_dict.get('content', {})

        # Validate content size (32KB limit)
        content_json_str = json.dumps(content_dict)
        if len(content_json_str.encode('utf-8')) > 32768:
            raise ValueError(f"Content size exceeds 32KB limit")

        async with pool.acquire() as conn:
            # Use ON CONFLICT DO NOTHING to handle duplicate IDs gracefully
            await conn.execute(
                """
                INSERT INTO chat_thread_items (id, thread_id, type, role, content, created_at, n_tokens)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7)
                ON CONFLICT (id) DO NOTHING
                """,
                item.id,
                thread_id,
                item.type,
                getattr(item, 'role', None),
                content_json_str,
                item.created_at,
                getattr(item, 'n_tokens', None)
            )

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: Dict[str, Any]
    ) -> None:
        """Save or update an item in a thread.

        Args:
            thread_id: Thread identifier
            item: Thread item to save
            context: Request context
        """
        pool = await self.get_pool()

        # Convert item to dict using Pydantic's model_dump
        item_dict = item.model_dump(mode='json')
        content_dict = item_dict.get('content', {})

        # Validate content size (32KB limit)
        content_json_str = json.dumps(content_dict)
        if len(content_json_str.encode('utf-8')) > 32768:
            raise ValueError(f"Content size exceeds 32KB limit")

        async with pool.acquire() as conn:
            # Upsert: INSERT with ON CONFLICT UPDATE
            await conn.execute(
                """
                INSERT INTO chat_thread_items (id, thread_id, type, role, content, created_at, n_tokens)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    type = EXCLUDED.type,
                    role = EXCLUDED.role,
                    content = EXCLUDED.content,
                    n_tokens = EXCLUDED.n_tokens
                """,
                item.id,
                thread_id,
                item.type,
                getattr(item, 'role', None),
                content_json_str,
                item.created_at,
                getattr(item, 'n_tokens', None)
            )

    async def load_item(
        self, thread_id: str, item_id: str, context: Dict[str, Any]
    ) -> ThreadItem:
        """Load a specific item by ID.

        Args:
            thread_id: Thread identifier
            item_id: Item identifier
            context: Request context

        Returns:
            ThreadItem instance

        Raises:
            NotFoundError: If item doesn't exist
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, thread_id, type, role, content, created_at, n_tokens
                FROM chat_thread_items
                WHERE id = $1 AND thread_id = $2
                """,
                item_id,
                thread_id
            )

            if not row:
                raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

            # Parse JSONB content
            content = row["content"]
            if isinstance(content, str):
                content = json.loads(content)

            # Build item data with required fields
            item_data = {
                "id": row["id"],
                "thread_id": thread_id,
                "type": row["type"],
                "content": content,
                "created_at": row["created_at"]
            }

            # Add role if present
            if row["role"]:
                item_data["role"] = row["role"]

            # Add inference_options for message types
            if row["type"] in ("user_message", "assistant_message"):
                item_data["inference_options"] = {}

            return self._thread_item_adapter.validate_python(item_data)

    async def delete_thread(self, thread_id: str, context: Dict[str, Any]) -> None:
        """Delete a thread and all its items.

        Args:
            thread_id: Thread identifier
            context: Request context
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM chat_threads WHERE id = $1",
                thread_id
            )

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: Dict[str, Any]
    ) -> None:
        """Delete a specific item from a thread.

        Args:
            thread_id: Thread identifier
            item_id: Item identifier
            context: Request context
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM chat_thread_items WHERE id = $1 AND thread_id = $2",
                item_id,
                thread_id
            )

    # Attachment methods - not implemented for this feature
    async def save_attachment(
        self, attachment: Attachment, context: Dict[str, Any]
    ) -> None:
        """Attachments not implemented in this phase."""
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(
        self, attachment_id: str, context: Dict[str, Any]
    ) -> Attachment:
        """Attachments not implemented in this phase."""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(self, attachment_id: str, context: Dict[str, Any]) -> None:
        """Attachments not implemented in this phase."""
        raise NotImplementedError("Attachments not supported")
