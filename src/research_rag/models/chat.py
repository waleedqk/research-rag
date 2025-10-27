"""Models defining chat-oriented interactions."""

from pydantic import BaseModel


class Message(BaseModel):
    """Represents a single message in a conversational exchange."""


class ChatRequest(BaseModel):
    """Encapsulates a chat prompt along with runtime parameters."""
