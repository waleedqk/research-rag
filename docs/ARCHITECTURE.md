# Architecture Overview

## High-Level Design

The Research RAG Assistant is organized around clear boundaries separating domain logic, adapters, and presentation layers. The CLI acts as the primary interface, while the web application reuses the same services for HTTP access.

## Modules

- `research_rag.core`: configuration, logging, errors, and domain services.
- `research_rag.adapters`: integrations with external systems such as PDFs, CSVs, embeddings, vector stores, and LLM providers.
- `research_rag.models`: Pydantic data contracts shared across modules.
- `research_rag.cli`: Typer-powered command-line interface wiring.
- `research_rag.web`: FastAPI endpoints and a lightweight UI surface.
- `research_rag.utils`: shared helper utilities.

## Data Flow

1. **Ingestion** — PDFs and CSV metadata are loaded via adapters and normalized into Pydantic models.
2. **Indexing** — Documents are embedded and stored in a vector database for retrieval.
3. **Retrieval** — Search queries perform similarity lookups against the index.
4. **Generation** — Retrieved context is passed to the configured LLM provider to craft responses.

## Configuration Strategy

- `.env` captures environment-specific overrides and secrets.
- `config.yaml` defines defaults and feature flags.
- Runtime precedence follows CLI flags > environment variables > config defaults.

## Observability

- Logging is centralized through Loguru helpers for consistent formatting and context.
- Each CLI invocation or HTTP request attaches a request ID for traceability.
- Log level varies by profile (`APP_ENV`) and CLI `--debug` flag.

## Extensibility

- Provider interfaces enable swapping LLMs, embeddings, and vector stores without touching core services.
- Service classes coordinate workflows and expose testable units with clearly defined boundaries.
- The architecture favors dependency injection to simplify testing and runtime configuration.
