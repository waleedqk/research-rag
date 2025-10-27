"""Domain models describing research paper metadata and content."""

from pydantic import BaseModel


class Paper(BaseModel):
    """Structured metadata describing a research paper and its provenance."""


class PaperContent(BaseModel):
    """Full text assets extracted from a research paper."""


class Citation(BaseModel):
    """Represents a bibliographic reference associated with a paper."""


class IndexedDoc(BaseModel):
    """Describes a document as stored within the vector index."""
