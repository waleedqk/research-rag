"""OpenAI-backed implementation of the language model provider interface."""

from typing import Iterable

from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message


class OpenAILLMProvider(BaseLLMProvider):
    """Chat provider that proxies requests to OpenAI's API."""

    def chat(self, request: ChatRequest) -> Iterable[Message]:
        """Execute the chat completion workflow for OpenAI."""
        ...
