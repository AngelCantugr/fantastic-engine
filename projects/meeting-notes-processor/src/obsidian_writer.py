"""
Write meeting notes to Obsidian vault
"""
import os
import logging
from pathlib import Path
from datetime import datetime


logger = logging.getLogger(__name__)


class ObsidianWriter:
    """Writes meeting notes to Obsidian vault"""

    def __init__(self, vault_path: Path = None):
        if vault_path is None:
            vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH'))

        self.vault_path = vault_path
        self.meetings_folder = os.getenv('MEETING_NOTES_FOLDER', 'Meetings')
        self.organize_by_date = os.getenv('ORGANIZE_BY_DATE', 'false').lower() == 'true'

        # Create meetings folder
        self.meetings_path = vault_path / self.meetings_folder
        self.meetings_path.mkdir(parents=True, exist_ok=True)

    def write_note(self, title: str, content: str, date: str = None) -> Path:
        """
        Write meeting note to Obsidian

        Args:
            title: Meeting title
            content: Note content
            date: Meeting date (YYYY-MM-DD)

        Returns:
            Path to created note
        """
        # Sanitize title for filename
        filename = self._sanitize_filename(title)

        # Determine folder structure
        if self.organize_by_date and date:
            # Create YYYY/MM folder structure
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            year_folder = self.meetings_path / str(date_obj.year)
            month_folder = year_folder / f"{date_obj.month:02d}"
            month_folder.mkdir(parents=True, exist_ok=True)
            note_path = month_folder / f"{filename}.md"
        else:
            note_path = self.meetings_path / f"{filename}.md"

        # Write note
        logger.info(f"Writing note to {note_path}")
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return note_path

    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as filename"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')

        # Replace spaces with hyphens
        title = title.replace(' ', '-')

        # Limit length
        if len(title) > 100:
            title = title[:100]

        return title


if __name__ == '__main__':
    # Test writer
    writer = ObsidianWriter(Path('/path/to/vault'))

    content = """# Test Meeting

This is a test note.

## Action Items
- [ ] Test action
"""

    path = writer.write_note(
        title="Test Meeting - 2025-11-16",
        content=content,
        date="2025-11-16"
    )

    print(f"Note written to: {path}")
