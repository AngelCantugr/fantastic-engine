"""Obsidian integration for syncing Pomodoro sessions to daily notes."""
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console

from session_tracker import PomodoroSession
from config import get_config


console = Console()


class ObsidianSync:
    """Handles syncing Pomodoro sessions to Obsidian daily notes."""

    def __init__(self):
        """Initialize Obsidian sync."""
        self.config = get_config()
        self.vault_path = self.config.obsidian_vault_path
        self.daily_notes_folder = self.config.obsidian_daily_notes_folder
        self.enabled = self.config.obsidian_enabled

    def is_configured(self) -> bool:
        """Check if Obsidian integration is properly configured."""
        if not self.enabled:
            return False

        if not self.vault_path or not self.vault_path.exists():
            console.print("[yellow]Warning: Obsidian vault path not configured or doesn't exist[/yellow]")
            return False

        return True

    def get_daily_note_path(self, date: Optional[datetime] = None) -> Path:
        """Get the path to the daily note for a given date."""
        if date is None:
            date = datetime.now()

        if not self.vault_path:
            raise ValueError("Obsidian vault path not configured")

        # Format: YYYY-MM-DD.md
        note_name = date.strftime("%Y-%m-%d.md")

        # Full path
        daily_notes_path = self.vault_path / self.daily_notes_folder
        return daily_notes_path / note_name

    def ensure_daily_note_exists(self, date: Optional[datetime] = None) -> Path:
        """Ensure daily note exists, create if it doesn't."""
        note_path = self.get_daily_note_path(date)

        # Create directory if it doesn't exist
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not note_path.exists():
            date_str = (date or datetime.now()).strftime("%Y-%m-%d")
            initial_content = f"""# {date_str}

## Daily Notes

## Pomodoro Sessions

"""
            note_path.write_text(initial_content)
            console.print(f"[green]Created daily note: {note_path}[/green]")

        return note_path

    def append_session(self, session: PomodoroSession) -> bool:
        """Append a Pomodoro session to the daily note."""
        if not self.is_configured():
            console.print("[yellow]Obsidian sync not configured, skipping...[/yellow]")
            return False

        try:
            note_path = self.ensure_daily_note_exists(session.start_time)

            # Format session entry
            session_entry = self._format_session_entry(session)

            # Read existing content
            content = note_path.read_text()

            # Check if we need to add the Pomodoro Sessions section
            if "## Pomodoro Sessions" not in content:
                content += "\n## Pomodoro Sessions\n\n"

            # Append session entry
            # Find the Pomodoro Sessions section and append
            lines = content.split('\n')
            insert_index = -1

            for i, line in enumerate(lines):
                if line.strip() == "## Pomodoro Sessions":
                    # Find the next section or end of file
                    insert_index = i + 1
                    while insert_index < len(lines) and not lines[insert_index].startswith("## "):
                        insert_index += 1
                    break

            if insert_index != -1:
                lines.insert(insert_index, session_entry)
                content = '\n'.join(lines)
            else:
                content += session_entry

            # Write back
            note_path.write_text(content)

            console.print(f"[green]✓ Synced to Obsidian: {note_path.name}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error syncing to Obsidian: {e}[/red]")
            return False

    def _format_session_entry(self, session: PomodoroSession) -> str:
        """Format a session as Obsidian markdown."""
        time_str = session.start_time.strftime("%H:%M")
        duration_str = session.duration_display

        # Status emoji
        status_emoji = "✅" if session.completed else "⏸️"

        # Value rating
        value_str = ""
        if session.value_rating:
            stars = "⭐" * session.value_rating
            value_str = f" - {stars} ({session.value_rating}/5)"

        # Tags
        tags_str = ""
        if session.tags:
            tags_str = " " + " ".join(f"#{tag}" for tag in session.tags)

        # Notes
        notes_str = ""
        if session.notes:
            notes_str = f"\n  - {session.notes}"

        entry = f"""
- {status_emoji} **{time_str}** - {session.topic} ({duration_str}){value_str}{tags_str}{notes_str}
"""

        return entry

    def sync_multiple_sessions(self, sessions: list[PomodoroSession]) -> int:
        """Sync multiple sessions to Obsidian."""
        if not self.is_configured():
            console.print("[yellow]Obsidian sync not configured, skipping...[/yellow]")
            return 0

        synced_count = 0
        for session in sessions:
            if self.append_session(session):
                synced_count += 1

        return synced_count

    def get_daily_note_content(self, date: Optional[datetime] = None) -> Optional[str]:
        """Get the content of a daily note."""
        try:
            note_path = self.get_daily_note_path(date)
            if note_path.exists():
                return note_path.read_text()
            return None
        except Exception as e:
            console.print(f"[red]Error reading daily note: {e}[/red]")
            return None


def create_obsidian_sync() -> ObsidianSync:
    """Create an ObsidianSync instance."""
    return ObsidianSync()


def quick_sync_session(session: PomodoroSession) -> bool:
    """Quick function to sync a single session."""
    sync = create_obsidian_sync()
    return sync.append_session(session)
