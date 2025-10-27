"""Ollama-backed implementation of the language model provider interface."""

from typing import Iterable

from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message


class OllamaLLMProvider(BaseLLMProvider):
    """Chat provider that interacts with a locally hosted Ollama server."""

    def chat(self, request: ChatRequest) -> Iterable[Message]:
        """Execute the chat completion workflow for Ollama."""
        ...
