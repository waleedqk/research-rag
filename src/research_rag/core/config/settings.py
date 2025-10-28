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


class AppSettings(BaseModel):
    """Typed representation of application configuration sources."""

    data: DataSettings = Field(default_factory=DataSettings)


def load_settings(config_path: str | Path | None = None) -> AppSettings:
    """Load application settings from YAML and environment overrides."""

    config_file = Path(config_path) if config_path else Path("config.yaml")
    config_data: Dict[str, Any] = {}

    if config_file.exists() and yaml is not None:
        loaded = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            config_data = loaded

    data_block = config_data.get("data", {}) if isinstance(config_data, dict) else {}
    summary_csv_path = os.getenv("SUMMARY_CSV_PATH", data_block.get("summary_csv_path"))
    pdf_directory = os.getenv("PDF_DIRECTORY", data_block.get("pdf_directory"))

    settings = AppSettings(
        data=DataSettings(
            summary_csv_path=summary_csv_path,
            pdf_directory=pdf_directory,
        )
    )
    return settings
