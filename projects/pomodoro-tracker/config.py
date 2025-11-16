"""Configuration management for Pomodoro Tracker."""
from pathlib import Path
from typing import Optional
import os
from pydantic import BaseModel, Field


class PomodoroConfig(BaseModel):
    """Configuration settings for Pomodoro Tracker."""

    # Timer settings
    default_duration_minutes: int = Field(default=30, description="Default pomodoro duration in minutes")
    break_duration_minutes: int = Field(default=5, description="Break duration in minutes")
    long_break_duration_minutes: int = Field(default=15, description="Long break duration after 4 pomodoros")

    # Storage settings
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".pomodoro-sessions")
    sessions_file: str = Field(default="sessions.json")

    # Obsidian integration
    obsidian_vault_path: Optional[Path] = Field(default=None)
    obsidian_daily_notes_folder: str = Field(default="Daily Notes")
    obsidian_enabled: bool = Field(default=False)

    # UI settings
    enable_sound: bool = Field(default=True)
    enable_celebration: bool = Field(default=True)

    # Analytics
    working_hours_start: int = Field(default=6, description="Start of working hours (24h format)")
    working_hours_end: int = Field(default=22, description="End of working hours (24h format)")

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    @property
    def sessions_path(self) -> Path:
        """Get full path to sessions file."""
        return self.data_dir / self.sessions_file

    def ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_from_env(cls) -> "PomodoroConfig":
        """Load configuration from environment variables."""
        config = cls()

        # Load from environment
        if duration := os.getenv("POMODORO_DURATION"):
            config.default_duration_minutes = int(duration)

        if break_duration := os.getenv("POMODORO_BREAK"):
            config.break_duration_minutes = int(break_duration)

        if obsidian_vault := os.getenv("OBSIDIAN_VAULT_PATH"):
            config.obsidian_vault_path = Path(obsidian_vault)
            config.obsidian_enabled = True

        if obsidian_folder := os.getenv("OBSIDIAN_DAILY_NOTES_FOLDER"):
            config.obsidian_daily_notes_folder = obsidian_folder

        if data_dir := os.getenv("POMODORO_DATA_DIR"):
            config.data_dir = Path(data_dir)

        return config


# Global configuration instance
_config: Optional[PomodoroConfig] = None


def get_config() -> PomodoroConfig:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = PomodoroConfig.load_from_env()
        _config.ensure_data_dir()
    return _config


def reset_config() -> None:
    """Reset global configuration (useful for testing)."""
    global _config
    _config = None
