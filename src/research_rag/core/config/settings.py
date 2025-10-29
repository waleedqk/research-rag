"""Configuration schema definitions and loading helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    from research_rag.utils.pydantic_compat import BaseModel, Field

try:  # pragma: no cover - optional dependency for YAML parsing
    import yaml
except ModuleNotFoundError:  # pragma: no cover - fallback when PyYAML is absent
    yaml = None


class DataSettings(BaseModel):
    """Configuration block describing local data paths."""

    summary_csv_path: Optional[str] = None
    pdf_directory: Optional[str] = None
    output_directory: Optional[str] = None


class LLMSettings(BaseModel):
    """Runtime configuration for language model providers."""

    provider: str = "local"
    model: Optional[str] = None
    api_key: Optional[str] = None
    host: Optional[str] = None


class AppSettings(BaseModel):
    """Typed representation of application configuration sources."""

    data: DataSettings = Field(default_factory=DataSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)


def _load_yaml(config_file: Path) -> Dict[str, Any]:
    if config_file.exists() and yaml is not None:
        loaded = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            return loaded
    return {}


def load_settings(config_path: str | Path | None = None) -> AppSettings:
    """Load application settings from YAML and environment overrides."""

    config_file = Path(config_path) if config_path else Path("config.yaml")
    config_data = _load_yaml(config_file)

    data_block = config_data.get("data", {}) if isinstance(config_data, dict) else {}
    summary_csv_path = os.getenv("SUMMARY_CSV_PATH") or data_block.get("summary_csv_path")
    pdf_directory = os.getenv("PDF_DIRECTORY") or data_block.get("pdf_directory") or data_block.get(
        "source_dir"
    )
    output_directory = os.getenv("OUTPUT_DIRECTORY") or data_block.get("output_directory") or data_block.get(
        "derived_dir"
    )

    providers_block = config_data.get("providers", {}) if isinstance(config_data, dict) else {}
    llm_block = config_data.get("llm", {}) if isinstance(config_data, dict) else {}

    provider_value = (
        os.getenv("LLM_PROVIDER")
        or llm_block.get("provider")
        or providers_block.get("llm")
        or "local"
    )
    provider_value = str(provider_value).strip().lower() or "local"
    if provider_value not in {"openai", "ollama", "local"}:
        provider_value = "local"

    llm_model = os.getenv("LLM_MODEL") or llm_block.get("model")
    api_key = os.getenv("OPENAI_API_KEY") or llm_block.get("api_key")
    host = os.getenv("OLLAMA_HOST") or llm_block.get("host")

    settings = AppSettings(
        data=DataSettings(
            summary_csv_path=summary_csv_path,
            pdf_directory=pdf_directory,
            output_directory=output_directory,
        ),
        llm=LLMSettings(
            provider=provider_value,
            model=llm_model,
            api_key=api_key,
            host=host,
        ),
    )
    return settings
