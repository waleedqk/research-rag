"""Module enabling `python -m research_rag.cli` entry point."""

from dotenv import load_dotenv
from research_rag.cli.app import app


def run() -> None:
    """Invoke the Typer application."""
    load_dotenv()
    app()


if __name__ == "__main__":
    run()
