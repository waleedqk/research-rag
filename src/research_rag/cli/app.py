"""Typer application exposing the command-line interface."""

import typer

app = typer.Typer(help="CLI entry point for the Research RAG assistant.")


@app.callback()
def main(config: str = typer.Option(None, help="Path to a configuration file."), debug: bool = typer.Option(False, help="Enable verbose logging.")) -> None:
    """Root CLI callback responsible for wiring global options."""
    ...


@app.command()
def ingest(pdf: str = typer.Argument(..., help="Path to a research PDF."), csv: str = typer.Option(None, help="Optional CSV metadata file.")) -> None:
    """Placeholder for the ingestion command."""
    ...


@app.command()
def search(query: str = typer.Argument(..., help="Search query string."), top_k: int = typer.Option(5, help="Number of top results to return.")) -> None:
    """Placeholder for the search command."""
    ...


@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask the assistant."), top_k: int = typer.Option(5, help="Number of supporting documents to retrieve.")) -> None:
    """Placeholder for the question-answer command."""
    ...
