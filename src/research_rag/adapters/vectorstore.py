"""Interfaces for persisting and querying vector indices."""


class VectorStore:
    """Persists document embeddings for similarity search."""

    def add(self, documents):
        """Placeholder for adding documents into the vector index."""
        ...

    def search(self, query):
        """Placeholder for executing similarity search queries."""
        ...
