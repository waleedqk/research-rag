"""Abstract interface for chat-capable language model providers."""

from abc import ABC, abstractmethod
from typing import Iterable

from research_rag.models import ChatRequest, Message


class BaseLLMProvider(ABC):
    """Defines the contract all language model providers must satisfy."""

    @abstractmethod
    def chat(self, request: ChatRequest) -> Iterable[Message]:
        """Stream chat responses for the given request."""
        ...
