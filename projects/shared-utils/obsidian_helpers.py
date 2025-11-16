"""Obsidian markdown file operations and parsing."""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class ObsidianTask:
    """Represents a task from Obsidian markdown."""
    content: str
    completed: bool
    file_path: Path
    line_number: int
    tags: List[str]
    priority: Optional[int] = None
    due_date: Optional[date] = None


@dataclass
class ObsidianNote:
    """Represents an Obsidian note."""
    path: Path
    title: str
    content: str
    frontmatter: Dict[str, any]
    tasks: List[ObsidianTask]
    tags: List[str]
    links: List[str]
    modified: datetime


def read_note(file_path: Path) -> ObsidianNote:
    """Read and parse an Obsidian note."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter = parse_frontmatter(content)
    tasks = parse_tasks(content, file_path)
    tags = parse_tags(content)
    links = parse_links(content)
    title = file_path.stem

    # Extract title from frontmatter or first heading
    if "title" in frontmatter:
        title = frontmatter["title"]
    else:
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1)

    return ObsidianNote(
        path=file_path,
        title=title,
        content=content,
        frontmatter=frontmatter,
        tasks=tasks,
        tags=tags,
        links=links,
        modified=datetime.fromtimestamp(file_path.stat().st_mtime)
    )


def parse_frontmatter(content: str) -> Dict[str, any]:
    """Parse YAML frontmatter from markdown."""
    frontmatter = {}
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        try:
            import yaml
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except ImportError:
            # Fallback to simple key-value parsing
            for line in match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter


def parse_tasks(content: str, file_path: Path) -> List[ObsidianTask]:
    """Parse tasks from markdown content."""
    tasks = []
    lines = content.split('\n')

    task_pattern = r'^(\s*)-\s+\[([ x>])\]\s+(.+)$'

    for line_num, line in enumerate(lines, 1):
        match = re.match(task_pattern, line)
        if match:
            _, status, task_content = match.groups()

            # Parse tags from task content
            tags = re.findall(r'#([\w-]+)', task_content)

            # Parse priority (e.g., "!!!" or "🔴")
            priority = None
            if "!!!" in task_content:
                priority = 3
            elif "!!" in task_content:
                priority = 2
            elif "!" in task_content:
                priority = 1

            # Parse due date (e.g., "📅 2025-11-16" or "due: 2025-11-16")
            due_date = None
            date_match = re.search(r'(?:📅|due:)\s*(\d{4}-\d{2}-\d{2})', task_content)
            if date_match:
                try:
                    due_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                except ValueError:
                    pass

            tasks.append(ObsidianTask(
                content=task_content.strip(),
                completed=(status == 'x'),
                file_path=file_path,
                line_number=line_num,
                tags=tags,
                priority=priority,
                due_date=due_date
            ))

    return tasks


def parse_tags(content: str) -> List[str]:
    """Extract all tags from content."""
    return re.findall(r'#([\w-]+)', content)


def parse_links(content: str) -> List[str]:
    """Extract all wiki-style links from content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def find_notes_by_tag(vault_path: Path, tag: str) -> List[ObsidianNote]:
    """Find all notes containing a specific tag."""
    notes = []
    for md_file in vault_path.rglob("*.md"):
        note = read_note(md_file)
        if tag in note.tags:
            notes.append(note)
    return notes


def find_notes_modified_since(vault_path: Path, since: datetime) -> List[ObsidianNote]:
    """Find all notes modified since a given datetime."""
    notes = []
    for md_file in vault_path.rglob("*.md"):
        if datetime.fromtimestamp(md_file.stat().st_mtime) > since:
            notes.append(read_note(md_file))
    return notes


def get_recent_notes(vault_path: Path, days: int = 7) -> List[ObsidianNote]:
    """Get notes modified in the last N days."""
    since = datetime.now() - timedelta(days=days)
    return find_notes_modified_since(vault_path, since)


def create_daily_note(vault_path: Path, date_obj: Optional[date] = None) -> Path:
    """Create or get path for a daily note."""
    if date_obj is None:
        date_obj = date.today()

    daily_notes_dir = vault_path / "Daily Notes"
    daily_notes_dir.mkdir(exist_ok=True)

    note_path = daily_notes_dir / f"{date_obj.strftime('%Y-%m-%d')}.md"
    return note_path


def write_note(file_path: Path, title: str, content: str, frontmatter: Optional[Dict] = None):
    """Write an Obsidian note with optional frontmatter."""
    with open(file_path, 'w', encoding='utf-8') as f:
        if frontmatter:
            f.write("---\n")
            try:
                import yaml
                yaml.dump(frontmatter, f, default_flow_style=False)
            except ImportError:
                for key, value in frontmatter.items():
                    f.write(f"{key}: {value}\n")
            f.write("---\n\n")

        f.write(f"# {title}\n\n")
        f.write(content)


from datetime import timedelta
