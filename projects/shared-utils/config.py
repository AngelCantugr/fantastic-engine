"""Configuration management for all projects."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings for ADHD productivity tools."""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Paths
    obsidian_vault_path: Optional[Path] = None
    ticktick_mcp_url: str = "http://localhost:3000"

    # Database
    postgres_url: Optional[str] = None
    redis_url: str = "redis://localhost:6379"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_obsidian_vault() -> Path:
    """Get Obsidian vault path from environment or default."""
    settings = get_settings()
    if settings.obsidian_vault_path:
        return settings.obsidian_vault_path

    # Try common locations
    home = Path.home()
    common_locations = [
        home / "Documents" / "Obsidian",
        home / "Obsidian",
        home / "Notes",
    ]

    for location in common_locations:
        if location.exists():
            return location

    raise ValueError(
        "Could not find Obsidian vault. Set OBSIDIAN_VAULT_PATH environment variable."
    )
