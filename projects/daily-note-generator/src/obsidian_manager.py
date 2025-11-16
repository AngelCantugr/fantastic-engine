"""
Obsidian vault manager for reading and writing daily notes
"""
import os
import logging
from pathlib import Path
from datetime import date
from typing import Optional


logger = logging.getLogger(__name__)


class ObsidianManager:
    """Manages reading and writing Obsidian daily notes"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.daily_notes_folder = os.getenv('DAILY_NOTES_FOLDER', 'Daily Notes')
        self.note_format = os.getenv('DAILY_NOTE_FORMAT', 'YYYY-MM-DD')

        # Create daily notes folder if it doesn't exist
        self.daily_notes_path = vault_path / self.daily_notes_folder
        self.daily_notes_path.mkdir(parents=True, exist_ok=True)

    def _format_date(self, target_date: date) -> str:
        """Format date according to configured format"""
        # Simple implementation - can be extended for more formats
        if self.note_format == 'YYYY-MM-DD':
            return target_date.strftime('%Y-%m-%d')
        elif self.note_format == 'YYYY/MM/YYYY-MM-DD':
            return f"{target_date.year}/{target_date.month:02d}/{target_date.strftime('%Y-%m-%d')}"
        else:
            # Default to ISO format
            return target_date.strftime('%Y-%m-%d')

    def get_note_path(self, target_date: date) -> Path:
        """Get path to daily note"""
        filename = f"{self._format_date(target_date)}.md"

        # Handle nested folder formats
        if '/' in self._format_date(target_date):
            parts = self._format_date(target_date).split('/')
            folder = self.daily_notes_path / '/'.join(parts[:-1])
            folder.mkdir(parents=True, exist_ok=True)
            return folder / f"{parts[-1]}.md"

        return self.daily_notes_path / filename

    def note_exists(self, target_date: date) -> bool:
        """Check if note exists for date"""
        return self.get_note_path(target_date).exists()

    def read_note(self, target_date: date) -> Optional[str]:
        """Read daily note content"""
        note_path = self.get_note_path(target_date)

        if not note_path.exists():
            logger.info(f"No note found for {target_date}")
            return None

        logger.info(f"Reading note from {note_path}")
        with open(note_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_note(self, target_date: date, content: str):
        """Write daily note"""
        note_path = self.get_note_path(target_date)

        logger.info(f"Writing note to {note_path}")
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def extract_completed_tasks(self, note_content: str) -> list:
        """Extract completed tasks from note"""
        import re

        if not note_content:
            return []

        # Find all completed tasks [x]
        pattern = r'- \[x\] (.+)'
        matches = re.findall(pattern, note_content)
        return matches

    def extract_notes_section(self, note_content: str) -> Optional[str]:
        """Extract the Notes section from daily note"""
        import re

        if not note_content:
            return None

        # Find Notes section
        pattern = r'## 📝 Notes\s+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, note_content, re.DOTALL)

        if match:
            notes = match.group(1).strip()
            return notes if notes else None

        return None


if __name__ == '__main__':
    # Test the manager
    from datetime import datetime

    vault = Path('/path/to/vault')
    manager = ObsidianManager(vault)

    # Test path generation
    today = datetime.now().date()
    path = manager.get_note_path(today)
    print(f"Note path: {path}")

    # Test reading
    content = manager.read_note(today)
    if content:
        completed = manager.extract_completed_tasks(content)
        print(f"Completed tasks: {completed}")

        notes = manager.extract_notes_section(content)
        print(f"Notes: {notes}")
