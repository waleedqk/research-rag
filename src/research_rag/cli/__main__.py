"""Module enabling `python -m research_rag.cli` entry point."""

from research_rag.cli.app import app


def run() -> None:
    """Invoke the Typer application."""
    app()


if __name__ == "__main__":
    run()
