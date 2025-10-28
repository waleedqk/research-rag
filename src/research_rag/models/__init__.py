"""Data models describing shared application contracts."""

from .papers import PaperRelevanceResponse, PaperRelevanceScore, PaperSummary
from .search import SearchFilters, SearchHit, SearchQuery
from .chat import ChatRequest, Message

__all__ = [
    "PaperSummary",
    "PaperRelevanceScore",
    "PaperRelevanceResponse",
    "SearchFilters",
    "SearchHit",
    "SearchQuery",
    "ChatRequest",
    "Message",
]
