# Research RAG Assistant

![Build Status](https://img.shields.io/badge/status-prealpha-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Research RAG Assistant is a CLI-first productivity tool for working with research PDFs and their companion CSV summaries. It ingests local documents, builds searchable indices, and supports retrieval-augmented generation (RAG) question answering. Every capability is implemented for the terminal first and then exposed via a thin web experience that reuses the same services. The assistant is provider-agnostic, allowing you to swap between OpenAI and Ollama at runtime.

## Features

- CLI-first workflows for ingestion, search, and question answering.
- Thin FastAPI web layer that mirrors the CLI experience.
- Pluggable provider interfaces for OpenAI and Ollama.
- Typed Pydantic models defining all cross-module contracts.
- Structured logging with per-request context.
- Configurable via `.env` and `config.yaml` profiles.

### Roadmap Highlights

- Implement PDF and CSV ingestion pipelines.
- Build vector index management and retrieval workflows.
- Add end-to-end integration tests with provider fakes.
- Polish the web UI with live search and chat views.

## Getting Started

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Installation

```bash
# Clone the repository
$ git clone https://github.com/your-org/research-rag.git
$ cd research-rag

# Install uv (if you don't have it yet)
$ python3 -m pip install uv

# Create a virtual environment in a desired location, for example:
$ python3 -m uv venv ~/uvs/research-rag-venv

# Activate the virtual environment
$ source ~/uvs/research-rag-venv/bin/activate

# Install dependencies
$ uv sync
```

### Configuration

```bash
# Copy the example environment file
$ cp .env.example .env

# Edit configuration defaults
$ ${EDITOR:-nano} config.yaml
```

Configuration precedence: CLI flags > environment variables > `config.yaml` defaults. Set `APP_ENV` to `dev`, `test`, or `prod` to toggle profiles.

## CLI Usage

All commands support the global `--config` and `--debug` options.

```bash
# View CLI help
$ uv run research-rag --help

# Ingest documents (placeholder)
$ uv run research-rag ingest /path/to/paper.pdf --csv /path/to/metadata.csv

# Search indexed documents (placeholder)
$ uv run research-rag search "attention is all you need" --top-k 5

# Ask a question (placeholder)
$ uv run research-rag ask "Summarize the main contributions" --top-k 5
```

## Web API

- `GET /health` — liveness probe
- `GET /search?q=...&top_k=...` — returns an array of `SearchHit`
- `POST /ask` — accepts `{ "q": str, "top_k": int }` and returns `{ "answer": str }`

The web UI is a thin layer over the same services used by the CLI.

## Configuration Profiles

- `.env`: machine-specific paths, API keys, secrets (never committed).
- `config.yaml`: shared defaults, feature flags, and provider preferences.
- Environment variable `APP_ENV` selects between `dev`, `test`, and `prod` profiles.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for an in-depth overview of modules, data flow, and extension points.

## Data Directories

- `data/source`: raw PDFs and CSV files (ignored by git).
- `data/derived`: generated assets such as embeddings and indices (ignored by git).

## Logging & Troubleshooting

- Logs are written to `.logs/app.log` with structured formatting.
- Increase verbosity with the `--debug` flag on CLI commands.
- Each request is tagged with a request ID to simplify correlation.

## Contributing

1. Fork the repository and create a feature branch.
2. Run formatters and linters before submitting (`make fmt`, `make lint`).
3. Add unit tests for new functionality (`make test`).
4. Open a pull request with a clear description of changes.

## License

This project is released under the [MIT License](LICENSE).
