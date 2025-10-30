"""OpenAI-backed implementation of the language model provider interface."""

import os
from typing import Iterable
from urllib import response

from openai import OpenAI
from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message


class OpenAILLMProvider(BaseLLMProvider):
    """Chat provider that proxies requests to OpenAI's API."""

    def __init__(self, *, model: str, api_key: str | None = None) -> None:
        self.model = model
        # load the key from the env if not provided
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") if api_key is None else api_key)

    def chat(self, request: ChatRequest) -> Iterable[Message]:
        """Execute the chat completion workflow for OpenAI."""
        messages = [message.model_dump() for message in request.messages]

        use_stream = False  # True to enable streaming

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=use_stream,
        )

        if use_stream:
            for chunk in response:
                if content := chunk.choices[0].delta.content:
                    yield Message(role="assistant", content=content)
        else:
            content = response.choices[0].message.content
            yield Message(role="assistant", content=content)