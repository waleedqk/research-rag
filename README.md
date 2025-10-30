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

### Setup

1. Clone the repository and move into the project directory.
2. Copy `.env.example` to `.env` and adjust values if desired. By default the file pins `UV_PROJECT_ENVIRONMENT=.venv/uv`, which tells `uv` exactly where to create the virtual environment for this project.
3. Install [uv](https://github.com/astral-sh/uv) if you have not already done so (`python3 -m pip install uv`).
4. Source the `.env` file to export the virtual environment path and other configuration defaults.
5. Run `uv sync` to create/populate the environment at `UV_PROJECT_ENVIRONMENT`.
6. Activate the environment so the `research-rag` CLI is available on your `$PATH`.

```bash
git clone https://github.com/your-org/research-rag.git
cd research-rag

cp .env.example .env

# Auto-export all following variables
# Then stop auto-exporting variables
set -a
source .env
set +a

env | grep UV_PROJECT_ENVIRONMENT

# installs dependencies into the path defined by UV_PROJECT_ENVIRONMENT
uv sync

# make the CLI script available
source "$UV_PROJECT_ENVIRONMENT/bin/activate"
```

Configuration precedence: CLI flags > environment variables > `config.yaml` defaults. Set `APP_ENV` to `dev`, `test`, or `prod` to toggle profiles. Update `OPENAI_API_KEY` in your `.env` file and switch `LLM_PROVIDER` to `openai` (or `ollama`) if you want to call an external model instead of the built-in local scorer.

### Sample data

The repository includes a tiny CSV in `data/examples/computer_vision.csv` that you can use to smoke-test the relevance workflow. Running the relevance command will also write a JSON summary to `data/derived/relevance/` (configurable via `OUTPUT_DIRECTORY` or the `--output-dir` flag).

## CLI Usage

All commands support the global `--config` and `--debug` options.

```bash
# View CLI help (environment must be activated first)
$ research-rag --help

# Rank paper relevance for a query using the sample CSV
$ research-rag --debug relevance "self-supervised learning for computer vision" data/examples/computer_vision.csv

# Limit results and override the output directory
$ research-rag relevance "self-supervised learning for computer vision" \
    data/examples/computer_vision.csv --top-k 3 --output-dir ./data/derived/custom

# Ingest documents (placeholder)
$ research-rag ingest /path/to/paper.pdf --csv /path/to/metadata.csv

# Search indexed documents (placeholder)
$ research-rag search "attention is all you need" --top-k 5

# Ask a question (placeholder)
$ research-rag ask "Summarize the main contributions" --top-k 5
```

## Web API

- `GET /health` — liveness probe
- `GET /search?q=...&top_k=...` — returns an array of `SearchHit`
- `POST /ask` — accepts `{ "q": str, "top_k": int }` and returns `{ "answer": str }`

The web UI is a thin layer over the same services used by the CLI.

## Configuration Profiles

Configuration is loaded from the following sources, in order of precedence:

1.  **Environment variables**: Highest precedence. Use these for secrets and machine-specific settings.
2.  **`.env` file**: Loads environment variables from a file. Ideal for local development.
3.  **`config.yaml`**: Lowest precedence. Used for shared, non-sensitive defaults.

- **`.env`**: Used for machine-specific settings and secrets. This file should never be committed to version control. It's the best place for `OPENAI_API_KEY`, and to specify your `LLM_PROVIDER` and `LLM_MODEL` for local development.
- **`config.yaml`**: Contains shared defaults for the project, such as data directories and feature flags. This file is version controlled.

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
