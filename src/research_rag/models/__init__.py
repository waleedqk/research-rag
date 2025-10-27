"""Pydantic models describing shared data contracts."""

from .papers import Citation, IndexedDoc, Paper, PaperContent
from .search import SearchFilters, SearchHit, SearchQuery
from .chat import ChatRequest, Message

__all__ = [
    "Citation",
    "IndexedDoc",
    "Paper",
    "PaperContent",
    "SearchFilters",
    "SearchHit",
    "SearchQuery",
    "ChatRequest",
    "Message",
]
