"""Models representing search queries and results."""

from pydantic import BaseModel


class SearchFilters(BaseModel):
    """Optional filtering directives applied to a search query."""


class SearchQuery(BaseModel):
    """User search input paired with optional filters and configuration."""


class SearchHit(BaseModel):
    """A single ranked result returned from the search subsystem."""
