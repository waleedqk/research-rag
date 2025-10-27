"""FastAPI application exposing the web interface."""

from fastapi import FastAPI

app = FastAPI(title="Research RAG Assistant")


@app.get("/health")
async def health():
    """Health check endpoint placeholder."""
    ...


@app.get("/search")
async def search(q: str, top_k: int = 5):
    """Placeholder endpoint mirroring the CLI search command."""
    ...


@app.post("/ask")
async def ask(payload: dict):
    """Placeholder endpoint wrapping the chat service."""
    ...
