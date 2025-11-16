"""Obsidian notes collector."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import sys

# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared_utils.obsidian_helpers import (
    ObsidianNote,
    read_note,
    find_notes_modified_since
)


class ObsidianCollector:
    """Collects context from Obsidian notes."""

    def __init__(self, vault_path: Optional[Path] = None):
        if vault_path is None:
            from shared_utils.config import get_obsidian_vault
            vault_path = get_obsidian_vault()

        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault not found: {vault_path}")

    def get_recent_notes(self, days: int = 1) -> List[ObsidianNote]:
        """Get notes modified in the last N days."""
        since = datetime.now() - timedelta(days=days)
        return find_notes_modified_since(self.vault_path, since)

    def get_recent_daily_notes(self, count: int = 3) -> List[ObsidianNote]:
        """Get the most recent daily notes."""
        daily_notes_dir = self.vault_path / "Daily Notes"

        if not daily_notes_dir.exists():
            # Try alternative locations
            for alt_dir in ["daily", "dailies", "journal"]:
                alt_path = self.vault_path / alt_dir
                if alt_path.exists():
                    daily_notes_dir = alt_path
                    break

        if not daily_notes_dir.exists():
            return []

        # Get all markdown files, sort by modification time
        daily_files = sorted(
            daily_notes_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        notes = []
        for file_path in daily_files[:count]:
            try:
                notes.append(read_note(file_path))
            except Exception:
                continue

        return notes

    def get_active_tasks(self) -> List[str]:
        """Get all incomplete tasks from recent notes."""
        recent_notes = self.get_recent_notes(days=7)

        tasks = []
        for note in recent_notes:
            for task in note.tasks:
                if not task.completed:
                    tasks.append(task.content)

        return tasks

    def get_notes_by_tag(self, tag: str) -> List[ObsidianNote]:
        """Get notes with a specific tag."""
        notes = []
        for md_file in self.vault_path.rglob("*.md"):
            try:
                note = read_note(md_file)
                if tag in note.tags:
                    notes.append(note)
            except Exception:
                continue
        return notes

    def summarize_notes(self, notes: List[ObsidianNote]) -> str:
        """Create a text summary of notes for AI processing."""
        if not notes:
            return "No recent notes found."

        summary_parts = []

        for note in notes:
            # Note header
            summary_parts.append(f"## {note.title}")
            summary_parts.append(f"*Modified: {note.modified.strftime('%Y-%m-%d %H:%M')}*")

            # Tags
            if note.tags:
                summary_parts.append(f"*Tags: {', '.join(note.tags)}*")

            # Incomplete tasks
            incomplete_tasks = [t.content for t in note.tasks if not t.completed]
            if incomplete_tasks:
                summary_parts.append("\n**Incomplete Tasks:**")
                for task in incomplete_tasks[:5]:  # Limit to 5 tasks per note
                    summary_parts.append(f"- [ ] {task}")

            # Content snippet (first 500 chars)
            content_preview = note.content[:500].replace('\n', ' ').strip()
            if len(note.content) > 500:
                content_preview += "..."
            summary_parts.append(f"\n**Content:** {content_preview}")

            summary_parts.append("")  # Blank line between notes

        return "\n".join(summary_parts)
