.PHONY: setup lock fmt lint test run web

setup:
@echo "Install dependencies with uv sync"

lock:
@echo "Refresh dependency lockfile"

fmt:
@echo "Run ruff for formatting"

lint:
@echo "Run ruff and mypy checks"

test:
@echo "Run pytest suite"

run:
@echo "Display CLI help entry point"

web:
@echo "Start FastAPI server in development mode"
