"""Typer application exposing the command-line interface."""

from src.research_rag.core.config import settings
import typer
from pathlib import Path
from research_rag.core.config.settings import load_settings


app = typer.Typer(help="CLI entry point for the Research RAG assistant.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: str = typer.Option(None, help="Path to a configuration file."),
    debug: bool = typer.Option(False, help="Enable verbose logging."),
) -> None:
    """Root CLI callback responsible for wiring global options."""
    ctx.obj = load_settings(config)


@app.command()
def ingest(
    pdf: str = typer.Argument(..., help="Path to a research PDF."),
    csv: str = typer.Option(None, help="Optional CSV metadata file."),
) -> None:
    """Placeholder for the ingestion command."""
    ...


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query string."),
    top_k: int = typer.Option(5, help="Number of top results to return."),
) -> None:
    """Placeholder for the search command."""
    ...


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the assistant."),
    top_k: int = typer.Option(
        5, help="Number of supporting documents to retrieve."
    ),
) -> None:
    """Placeholder for the question-answer command."""
    ...


@app.command()
def relevance(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="The user's query for relevance ranking."),
    csv_path: Path = typer.Argument(
        ..., help="Path to the CSV file with paper metadata."
    ),
) -> None:
    """Ranks papers from a CSV file based on a query."""
    from research_rag.adapters.llm_providers.ollama import OllamaLLMProvider, OpenAILLMProvider
    from research_rag.core.services.relevance import PaperRelevanceService

    # settings = ctx.obj
    # Now you can use settings to configure your provider, e.g.:
    # llm_provider = OllamaLLMProvider(model=settings.llm.model)

    # This is a simplified setup. In a real app, you'd get this from config.
    llm_provider = OpenAILLMProvider(model="llama3", api_key=settings.llm.api_key)
    service = PaperRelevanceService(llm_provider=llm_provider)

    try:
        response = service.rank_papers(query=query, csv_path=csv_path)
        if not response.results:
            print("No relevant papers found.")
            return

        print(f"Found {len(response.results)} relevant papers for '{query}':")
        for result in response.results:
            print(f"  - {result.paper_title} (Score: {result.score:.2f})")

        if response.output_path:
            print(f"\nResults saved to: {response.output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
