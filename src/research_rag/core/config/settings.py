"""Configuration schema definitions and loading helpers."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSettings(BaseModel):
    """Configuration block describing local data paths."""

    source_dir: str = "data/source"
    derived_dir: str = "data/derived"
    output_directory: str = "data/derived/relevance"


class AppSettings(BaseSettings):
    """Typed representation of application configuration sources."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        # case_sensitive=False,  # uncomment if you want case-insensitive env keys
    )

    data: DataSettings = Field(default_factory=DataSettings)

    # LLM settings — bind to concrete env var names via validation_alias
    llm_provider: str = Field(
        default="local", validation_alias=AliasChoices("LLM_PROVIDER")
    )
    llm_model: str | None = Field(
        default=None, validation_alias=AliasChoices("LLM_MODEL")
    )
    llm_api_key: str | None = Field(
        default=None, validation_alias=AliasChoices("OPENAI_API_KEY")
    )
    llm_host: str | None = Field(
        default=None, validation_alias=AliasChoices("OLLAMA_HOST")
    )

def load_settings(config_path: str | Path | None = None) -> AppSettings:
    """Load application settings from YAML and environment overrides."""

    load_dotenv(dotenv_path=".env", override=True)

    config_file = Path(config_path) if config_path else Path("config.yaml")
    yaml_config: Dict[str, Any] = {}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f) or {}

    # Instantiate from env vars first.
    env_settings = AppSettings()
    env_dict = env_settings.model_dump()

    # Pop the 'data' dictionaries to merge them separately.
    yaml_data = yaml_config.pop("data", {}) or {}
    env_data = env_dict.pop("data", {}) or {}
    merged_data = {**yaml_data, **env_data}

    # Pass merged data and the rest of the configs to AppSettings.
    # The kwargs from env_dict will override yaml_config.
    settings = AppSettings(data=merged_data, **yaml_config, **env_dict)

    logger.debug(f"Loaded settings: {settings.model_dump_json(indent=2)}")
    return settings