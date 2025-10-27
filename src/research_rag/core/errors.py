"""Custom exception hierarchy for domain-specific errors."""


class ResearchRAGError(Exception):
    """Base exception for all custom errors in the assistant."""


class PDFNotFound(ResearchRAGError):
    """Raised when an expected PDF source cannot be located."""


class EmbeddingProviderError(ResearchRAGError):
    """Raised when an embedding provider experiences an unrecoverable issue."""


class IndexNotReady(ResearchRAGError):
    """Raised when search is requested before an index has been prepared."""
