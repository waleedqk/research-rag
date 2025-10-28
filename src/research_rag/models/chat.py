"""Models defining chat-oriented interactions."""

from __future__ import annotations

from typing import List, Literal, Optional, Tuple

try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, Field, validator
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    from research_rag.utils.pydantic_compat import BaseModel, Field, validator


VALID_ROLES: Tuple[Literal["system", "user", "assistant"], ...] = (
    "system",
    "user",
    "assistant",
)


class Message(BaseModel):
    """Represents a single message in a conversational exchange."""

    role: Literal["system", "user", "assistant"]
    content: str

    @validator("content")
    def _validate_content(cls, value: str) -> str:  # noqa: D401 - short validator description
        """Ensure message content is a non-empty string."""

        if not value or not value.strip():
            raise ValueError("Message content must be a non-empty string.")
        return value


class ChatRequest(BaseModel):
    """Encapsulates a chat prompt along with runtime parameters."""

    messages: List[Message] = Field(default_factory=list)
    temperature: float = 0.2
    max_tokens: Optional[int] = None

    @validator("messages")
    def _validate_messages(cls, value: List[Message]) -> List[Message]:
        if not value:
            raise ValueError("ChatRequest requires at least one message.")
        return value

    @validator("temperature")
    def _validate_temperature(cls, value: float) -> float:
        if not (0.0 <= value <= 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0.")
        return value

    @validator("max_tokens")
    def _validate_max_tokens(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("max_tokens must be positive when provided.")
        return value
