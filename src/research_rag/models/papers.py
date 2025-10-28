"""Simplified data models for ranking paper relevance."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, Field, validator
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    from research_rag.utils.pydantic_compat import BaseModel, Field, validator


class PaperSummary(BaseModel):
    """Lightweight representation of a CSV row describing a paper."""

    title: str
    columns: Dict[str, Optional[str]] = Field(default_factory=dict)

    @validator("title")
    def _validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("CSV rows must include a non-empty 'title' column")
        return value

    @classmethod
    def from_row(cls, row: dict[str, Optional[str]]) -> "PaperSummary":
        normalized = {str(key): value for key, value in row.items() if key is not None}
        title = normalized.get("title")
        if title is None:
            raise ValueError("CSV row is missing required 'title' column")
        return cls(title=title, columns=normalized)


class PaperRelevanceScore(BaseModel):
    """Structured representation of a paper relevance score."""

    paper_title: str
    score: float

    @validator("paper_title")
    def _validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Paper title cannot be empty")
        return value.strip()

    @validator("score")
    def _validate_score(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("Score must be between 0.0 and 1.0")
        return float(value)


class PaperRelevanceResponse(BaseModel):
    """Response container describing highly relevant papers for a query."""

    query: str
    results: List[PaperRelevanceScore] = Field(default_factory=list)
    output_path: Optional[Path] = None

    def as_2d_list(self) -> List[List[float | str]]:
        """Return the results as a 2D list ``[[paper_title, score], ...]``."""

        return [[result.paper_title, result.score] for result in self.results]
