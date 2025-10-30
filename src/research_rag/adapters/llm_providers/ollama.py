"""Ollama-backed implementation of the language model provider interface."""

from typing import Iterable, cast

import ollama
from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message


class OllamaLLMProvider(BaseLLMProvider):
    """Chat provider that interacts with a locally hosted Ollama server."""

    def __init__(
        self,
        *,
        model: str,
        host: str | None = None,
        timeout: int | None = 30,
    ) -> None:
        self.model = model
        self.client = ollama.Client(host=host, timeout=timeout)

    def chat(self, request: ChatRequest) -> Iterable[Message]:
        """Execute the chat completion workflow for Ollama."""
        messages = [message.model_dump() for message in request.messages]

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.get("message", {})
            if content := delta.get("content"):
                yield Message(role="assistant", content=cast(str, content))