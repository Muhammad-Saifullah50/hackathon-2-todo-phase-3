# Data Model: AI-Powered Task Management Chatbot

**Date**: 2025-12-23
**Feature**: 007-ai-chatbot

This document defines the database schema for conversation and message persistence, extending the existing task management system.

---

## Entity Overview

The chatbot feature introduces two new core entities:
- **Conversation**: Represents a chat session between user and AI
- **Message**: Individual messages within a conversation

It also extends existing entities:
- **Task**: Add new fields (due_date, priority) - already exists from 005-task-management
- **Tag**: Task categorization - already exists from 006-landing-page-ui
- **Template**: Task templates for reuse - already exists from 006-landing-page-ui

---

## Entity Definitions

### 1. Conversation

Represents a chat session between a user and the chatbot. Stores conversation metadata but not the actual messages (see Message entity).

**Purpose**: Group related messages, enable conversation history browsing, track session metadata.

**Lifecycle**: Created when user starts new chat, persists indefinitely (never deleted), updated on new message.

#### Schema

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

#### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Conversation(SQLModel, table=True):
    """Chat session between user and AI assistant."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200, description="Optional conversation title (first message or AI-generated)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
```

#### Validation Rules

| Rule | Description |
|------|-------------|
| **id** | UUID v4, auto-generated, immutable |
| **user_id** | Must reference existing user, required |
| **title** | Optional, max 200 chars, can be null initially |
| **created_at** | Auto-set to UTC timestamp on creation, immutable |
| **updated_at** | Auto-updated on any message addition |

#### State Transitions

- **Created** → When user sends first message without conversation_id
- **Updated** → On every new message (updated_at timestamp changes)
- **Inactive** → No state change, conversations persist indefinitely

**No deletion**: Conversations are never deleted to maintain complete history.

---

### 2. Message

Represents a single message in a conversation (user or assistant message).

**Purpose**: Store conversation history, enable context loading, support message replay/export.

**Lifecycle**: Created when user sends message or assistant responds, persists indefinitely, never updated after creation.

#### Schema

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

#### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Literal

class Message(SQLModel, table=True):
    """Single message in a conversation."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: Literal["user", "assistant", "system"] = Field(max_length=20, description="Message sender: user, assistant, or system")
    content: str = Field(description="Message text content")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

#### Validation Rules

| Rule | Description |
|------|-------------|
| **id** | UUID v4, auto-generated, immutable |
| **conversation_id** | Must reference existing conversation, required |
| **user_id** | Must reference existing user, required (same as conversation owner) |
| **role** | Must be 'user', 'assistant', or 'system', required |
| **content** | Non-empty text, max length unlimited (TEXT), required |
| **created_at** | Auto-set to UTC timestamp, immutable |

#### Message Roles

- **user**: Message from the human user
- **assistant**: Response from the AI chatbot
- **system**: Internal system messages (rare, used for context/notifications)

#### Ordering

Messages are ordered by `created_at` timestamp within a conversation. The composite index `(conversation_id, created_at DESC)` ensures efficient retrieval of recent messages.

---

## Extended Entities

### 3. Task (Extended)

The existing Task entity from 005-task-management is extended with new fields to support chatbot functionality.

#### New Fields

```sql
-- Migration: Add new columns to tasks table
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high'));

CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

#### Updated SQLModel

```python
class Task(SQLModel, table=True):
    """Task with chatbot-added fields."""
    __tablename__ = "tasks"

    # Existing fields (from 005-task-management)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    status: Literal["pending", "completed"] = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)  # Soft delete

    # New fields for chatbot
    due_date: Optional[datetime] = Field(default=None, index=True, description="Task due date (parsed from natural language)")
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="Task priority level")

    # Relationships
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
```

#### Validation Rules for New Fields

| Field | Validation |
|-------|------------|
| **due_date** | Optional, must be future date when set, timezone-aware |
| **priority** | Must be 'low', 'medium', or 'high', defaults to 'medium' |

---

## Relationships

### Conversation ↔ Message

- **Type**: One-to-Many
- **Description**: One conversation has many messages
- **Cascade**: DELETE CASCADE - deleting conversation deletes all its messages
- **Foreign Key**: message.conversation_id → conversation.id

### User ↔ Conversation

- **Type**: One-to-Many
- **Description**: One user has many conversations
- **Cascade**: DELETE CASCADE - deleting user deletes all their conversations
- **Foreign Key**: conversation.user_id → user.id

### User ↔ Message

- **Type**: One-to-Many
- **Description**: One user has many messages (both sent and received assistant messages)
- **Cascade**: DELETE CASCADE - deleting user deletes all their messages
- **Foreign Key**: message.user_id → user.id
- **Note**: message.user_id always matches message.conversation.user_id (enforced in application layer)

### User ↔ Task

- **Type**: One-to-Many (existing relationship from 005-task-management)
- **Description**: One user has many tasks
- **Cascade**: DELETE CASCADE
- **Foreign Key**: task.user_id → user.id

---

## Entity Relationship Diagram

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1:N
     ├──────────┐
     │          │
     ▼          ▼
┌──────────┐  ┌──────────┐
│   Task   │  │Conversation│
└──────────┘  └────┬─────┘
               1:N │
                   ▼
              ┌─────────┐
              │ Message │
              └─────────┘
```

---

## Database Indexes

### Performance Optimization Strategy

All indexes are designed for the most common query patterns:

1. **Fetch recent conversations for user**: `(user_id, updated_at DESC)`
2. **Fetch messages for conversation**: `(conversation_id, created_at DESC)`
3. **Load last N messages for context**: Uses composite index above
4. **Find tasks by due date**: `(due_date)` where due_date IS NOT NULL
5. **Filter tasks by priority**: `(priority)`

### Index Summary

| Table | Index Name | Columns | Purpose |
|-------|-----------|---------|---------|
| conversations | idx_conversations_user_id | (user_id) | Filter by user |
| conversations | idx_conversations_updated_at | (updated_at DESC) | Sort by recent activity |
| conversations | idx_conversations_user_updated | (user_id, updated_at DESC) | User's recent conversations |
| messages | idx_messages_conversation_id | (conversation_id) | Filter by conversation |
| messages | idx_messages_created_at | (created_at DESC) | Global message ordering |
| messages | idx_messages_conversation_created | (conversation_id, created_at DESC) | Conversation timeline |
| messages | idx_messages_user_id | (user_id) | Filter by user |
| tasks | idx_tasks_due_date | (due_date) WHERE due_date IS NOT NULL | Find upcoming tasks |
| tasks | idx_tasks_priority | (priority) | Filter by priority |

---

## Data Access Patterns

### 1. Create New Conversation

```python
async def create_conversation(user_id: UUID) -> Conversation:
    """Create new conversation for user."""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### 2. Add Message to Conversation

```python
async def add_message(
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str
) -> Message:
    """Add message to conversation and update conversation timestamp."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message
```

### 3. Load Last N Messages for Context

```python
async def get_conversation_context(
    conversation_id: UUID,
    limit: int = 50
) -> list[Message]:
    """Get last N messages for AI context (oldest first)."""
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    messages = result.scalars().all()
    return list(reversed(messages))  # Return oldest first
```

### 4. Paginate Conversation History (UI)

```python
async def get_messages_paginated(
    conversation_id: UUID,
    page: int = 1,
    page_size: int = 20
) -> tuple[list[Message], int]:
    """Get paginated messages for UI (newest first)."""
    offset = (page - 1) * page_size

    # Get messages
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(query)
    messages = result.scalars().all()

    # Get total count
    count_query = (
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation_id)
    )
    total = await session.scalar(count_query)

    return list(reversed(messages)), total  # Return oldest first for display
```

### 5. Get User's Recent Conversations

```python
async def get_user_conversations(
    user_id: UUID,
    limit: int = 20
) -> list[Conversation]:
    """Get user's most recent conversations."""
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return result.scalars().all()
```

---

## Alembic Migration

```python
"""Add conversation and message tables for chatbot

Revision ID: xxx
Revises: previous_revision
Create Date: 2025-12-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers
revision = 'xxx'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', [sa.text('updated_at DESC')])
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', sa.text('updated_at DESC')])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role_valid')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', [sa.text('created_at DESC')])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', sa.text('created_at DESC')])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

    # Extend tasks table with new fields
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(20), server_default='medium', nullable=False))
    op.create_check_constraint('check_priority_valid', 'tasks', "priority IN ('low', 'medium', 'high')")
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])

def downgrade():
    # Drop task extensions
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_constraint('check_priority_valid', 'tasks')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')

    # Drop messages table
    op.drop_index('idx_messages_user_id', table_name='messages')
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('idx_conversations_user_updated', table_name='conversations')
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

---

## Data Volume Estimates

### Growth Projections

| Metric | Initial | 6 Months | 1 Year |
|--------|---------|----------|--------|
| **Users** | 100 | 1,000 | 5,000 |
| **Conversations/User** | 5 | 20 | 50 |
| **Messages/Conversation** | 20 | 50 | 100 |
| **Total Messages** | 10K | 1M | 25M |
| **Storage (Messages)** | ~2MB | ~200MB | ~5GB |

### Performance Considerations

- **50-Message Context Window**: Loads only last 50 messages per request, keeps response time <100ms
- **Pagination**: UI loads 20 messages at a time, prevents large result sets
- **Composite Indexes**: Optimized for (conversation_id, created_at) queries
- **Future Partitioning**: Consider partitioning messages table by month if >10M messages

---

**Data Model Complete**: All entities, relationships, indexes, and migration scripts defined.
