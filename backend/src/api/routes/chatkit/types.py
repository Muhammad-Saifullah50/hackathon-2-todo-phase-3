"""ChatKit types definitions."""

from typing import List, Optional

class ChatKitRequest:
    """Represents a ChatKit request."""

    def __init__(self, messages: List[dict], thread_id: Optional[str] = None):
        self.messages = messages
        self.thread_id = thread_id

    def __repr__(self):
        return f"ChatKitRequest(messages={self.messages}, thread_id={self.thread_id})"

class ChatKitMessage:
    """Represents a ChatKit message."""

    def __init__(self, role: str, content: str, metadata: Optional[dict] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"ChatKitMessage(role={self.role}, content={self.content}, metadata={self.metadata})"