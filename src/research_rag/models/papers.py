"""Simplified data models for ranking paper relevance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Iterable


try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, Field, validator, field_validator
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    from research_rag.utils.pydantic_compat import BaseModel, Field, validator

def _prettify_key(k: str) -> str:
    """snake/camel → Title Case labels."""
    if not k:
        return k
    # split camelCase → camel Case
    s = re.sub(r'(?<!^)(?=[A-Z])', ' ', k)
    # replace underscores/dashes with spaces
    s = re.sub(r'[_\-]+', ' ', s)
    return s.strip().title()


class PaperSummary(BaseModel):
    """Lightweight representation of a CSV row describing a paper."""

    title: str
    columns: Dict[str, Optional[str]] = Field(default_factory=dict)

    # v2-style validator
    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        value = (value or "").strip()
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

    def to_text(
        self,
        *,
        prefer_keys: Iterable[str] = ("abstract", "summary", "keywords", "methods", "results", "conclusion"),
        include_keys: Optional[Iterable[str]] = None,   # if set, only these (plus title)
        exclude_keys: Iterable[str] = ("title",),       # always skip these
        rename_map: Optional[Dict[str, str]] = None,    # optional label overrides
        max_value_chars: int = 800,                     # per-field cap
        max_chars: int = 3000                           # overall cap
    ) -> str:
        """
        Render a compact, labeled text for the LLM:
        Title first, then preferred fields (if present), then remaining fields
        in the original CSV order. All non-empty values only.
        """
        def ok(k: str, v: Optional[str]) -> bool:
            if v is None:
                return False
            if not (s := v.strip()):
                return False
            if include_keys is not None and k not in include_keys:
                return False
            if k in exclude_keys:
                return False
            return True

        lines: list[str] = [f"Title: {self.title.strip()}"]

        # Build ordered key list: preferred keys (present) + remaining in CSV order
        seen = set(["title"])
        ordered_keys: list[str] = []
        # preferred block
        for k in prefer_keys:
            if k in self.columns and k not in seen:
                ordered_keys.append(k); seen.add(k)
        # remaining in original order
        for k in self.columns.keys():
            if k not in seen:
                ordered_keys.append(k); seen.add(k)

        for k in ordered_keys:
            v = self.columns.get(k)
            if not ok(k, v):
                continue
            label = (rename_map.get(k) if rename_map else None) or _prettify_key(k)
            val = v.strip().replace("\r\n", "\n").replace("\r", "\n")
            if len(val) > max_value_chars:
                val = val[: max_value_chars - 1].rstrip() + "…"
            lines.append(f"{label}: {val}")

            # soft overall cap
            joined = "\n".join(lines)
            if len(joined) >= max_chars:
                return joined[: max_chars - 1].rstrip() + "…"

        return "\n".join(lines)

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
