"""Typer application exposing the command-line interface."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional
import typer

from research_rag.core.config import AppSettings, load_settings
from research_rag.core.logging.setup import configure_logging, get_logger
from research_rag.core.services.relevance import PaperRelevanceService

app = typer.Typer(help="CLI entry point for the Research RAG assistant.")
logger = get_logger(__name__)

class LLMProvider(str, Enum):
    """Supported LLM providers."""

    LOCAL = "local"
    OPENAI = "openai"
    OLLAMA = "ollama"

def _resolve_settings(ctx: typer.Context) -> AppSettings:
    settings: Optional[AppSettings] = ctx.obj
    if settings is None:
        settings = load_settings()
        ctx.obj = settings
    return settings


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: str = typer.Option(None, help="Path to a configuration file."),
    debug: bool = typer.Option(False, help="Enable verbose logging."),
) -> None:
    """Root CLI callback responsible for wiring global options."""
    configure_logging(debug)
    settings = load_settings(config)
    ctx.obj = settings


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
    provider: LLMProvider = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider to use for ranking.",
        case_sensitive=False,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to store JSON summaries (defaults to config or CSV parent).",
    ),
    top_k: int = typer.Option(
        5,
        "--top-k",
        "-k",
        min=1,
        help="Maximum number of results to display in the terminal.",
    ),
) -> None:
    """Ranks papers from a CSV file based on a query."""
    from importlib import import_module

    settings = _resolve_settings(ctx)

    provider_name = provider.value if provider else settings.llm_provider
    logger.debug(f"Using LLM provider: {provider_name}")
    llm_provider = None

    if provider_name == "openai":
        try:
            module = import_module("research_rag.adapters.llm_providers.openai")
            OpenAILLMProvider = getattr(module, "OpenAILLMProvider")
        except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime safeguard
            raise typer.BadParameter(
                "OpenAI provider requires the optional 'openai' dependency."
            ) from exc
        if not settings.llm_model:
            raise typer.BadParameter("LLM model must be configured for the OpenAI provider")
        llm_provider = OpenAILLMProvider(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
        )
    elif provider_name == "ollama":
        try:
            module = import_module("research_rag.adapters.llm_providers.ollama")
            OllamaLLMProvider = getattr(module, "OllamaLLMProvider")
        except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime safeguard
            raise typer.BadParameter(
                "Ollama provider requires the optional 'ollama' dependency."
            ) from exc
        if not settings.llm_model:
            raise typer.BadParameter("LLM model must be configured for the Ollama provider")
        llm_provider = OllamaLLMProvider(model=settings.llm_model, host=settings.llm_host)

    service = PaperRelevanceService(
        llm_provider=llm_provider,
        output_directory=output_dir or settings.data.output_directory,
    )

    try:
        response = service.rank_papers(
            query=query,
            csv_path=csv_path,
            output_dir=output_dir,
        )
        if not response.results:
            print("No relevant papers found.")
            return

        total = len(response.results)
        print(f"Found {total} relevant papers for '{query}':")
        for result in response.results[:top_k]:
            print(f"  - {result.paper_title} (Score: {result.score:.2f})")

        if response.output_path:
            print(f"\nResults saved to: {response.output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
