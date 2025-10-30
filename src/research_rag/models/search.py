"""Models representing search queries and results."""

from __future__ import annotations

from typing import Dict, List, Optional

try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, Field, validator
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    from research_rag.utils.pydantic_compat import BaseModel, Field, validator


class SearchFilters(BaseModel):
    """Optional filtering directives applied to a search query."""

    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    """User search input paired with optional filters and configuration."""

    query: str
    top_k: int = 5
    filters: Optional[SearchFilters] = None

    @validator("query")
    def _validate_query(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Search query cannot be empty")
        return value

    @validator("top_k")
    def _validate_top_k(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("top_k must be positive")
        return value


class SearchHit(BaseModel):
    """A single ranked result returned from the search subsystem."""

    doc_id: str
    score: float
    title: Optional[str] = None
    snippet: Optional[str] = None

    @validator("doc_id")
    def _validate_doc_id(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("SearchHit requires a doc_id")
        return value

    @validator("score")
    def _validate_score(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Score must be numeric")
        return float(value)
