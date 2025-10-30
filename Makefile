.PHONY: setup lock fmt lint test run web

setup:
	@echo "Installing dependencies with uv..."
	set -a
	. .env
	set +a
	uv sync --quiet

lock:
	@echo "Refreshing dependency lockfile..."
	@uv lock

fmt:
	@echo "Formatting code with ruff..."
	@ruff format .

lint:
	@echo "Linting code with ruff and mypy..."
	@ruff check .
	@mypy .

test:
	@echo "Running tests with pytest..."
	@pytest

run:
	@echo "Running the research-rag CLI..."
	@research-rag

web:
	@echo "Starting the web server..."
	@uvicorn research_rag.web.api.app:app --reload
