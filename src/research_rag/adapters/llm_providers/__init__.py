"""Large language model provider interfaces and implementations."""

from __future__ import annotations

from .base import BaseLLMProvider

try:  # pragma: no cover - optional dependency
    from .ollama import OllamaLLMProvider
except ModuleNotFoundError:  # pragma: no cover - missing optional extra
    OllamaLLMProvider = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from .openai import OpenAILLMProvider
except ModuleNotFoundError:  # pragma: no cover - missing optional extra
    OpenAILLMProvider = None  # type: ignore[assignment]


__all__ = ["BaseLLMProvider"]

if OllamaLLMProvider is not None:  # pragma: no branch - simple guard
    __all__.append("OllamaLLMProvider")

if OpenAILLMProvider is not None:  # pragma: no branch - simple guard
    __all__.append("OpenAILLMProvider")
