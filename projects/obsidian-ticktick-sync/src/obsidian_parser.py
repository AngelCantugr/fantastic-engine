"""
Obsidian markdown parser for task extraction
"""
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import yaml


@dataclass
class Task:
    """Represents a task found in Obsidian"""
    content: str
    marker: str  # [ ], [x], [>], etc.
    line_number: int
    file_path: Path
    indent_level: int
    parent: Optional['Task'] = None
    children: List['Task'] = None
    tags: List[str] = None
    due_date: Optional[str] = None
    priority: int = 0

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.tags is None:
            self.tags = self._extract_tags()
        if self.due_date is None:
            self.due_date = self._extract_due_date()

    def _extract_tags(self) -> List[str]:
        """Extract #tags from content"""
        return re.findall(r'#([\w-]+)', self.content)

    def _extract_due_date(self) -> Optional[str]:
        """Extract due date from content (e.g., @due(2025-11-16))"""
        match = re.search(r'@due\((\d{4}-\d{2}-\d{2})\)', self.content)
        return match.group(1) if match else None

    @property
    def is_sync_marker(self) -> bool:
        """Check if task should be synced to TickTick"""
        return self.marker == '>'

    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.marker == 'x'

    @property
    def is_cancelled(self) -> bool:
        """Check if task is cancelled"""
        return self.marker == '-'


class ObsidianParser:
    """Parses Obsidian vault for tasks"""

    def __init__(self, vault_path: Path, config_path: Optional[Path] = None):
        self.vault_path = vault_path
        self.config = self._load_config(config_path)
        self.task_pattern = re.compile(r'^(\s*)- \[(.)\] (.+)$')

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load sync configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'sync_config.yaml'

        with open(config_path) as f:
            return yaml.safe_load(f)

    def get_files_to_sync(self) -> List[Path]:
        """Get all markdown files matching include patterns"""
        files = []
        include_patterns = self.config['sync_rules']['include_paths']
        exclude_patterns = self.config['sync_rules']['exclude_paths']

        for pattern in include_patterns:
            for file_path in self.vault_path.glob(pattern):
                if file_path.is_file() and not self._is_excluded(file_path, exclude_patterns):
                    files.append(file_path)

        return files

    def _is_excluded(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file matches exclude patterns"""
        relative_path = file_path.relative_to(self.vault_path)
        for pattern in exclude_patterns:
            if relative_path.match(pattern):
                return True
        return False

    def parse_file(self, file_path: Path) -> List[Task]:
        """Parse a single markdown file for tasks"""
        tasks = []
        task_stack = []  # Stack to track parent tasks

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            match = self.task_pattern.match(line)
            if not match:
                continue

            indent = match.group(1)
            marker = match.group(2)
            content = match.group(3).strip()

            indent_level = len(indent) // 2  # Assuming 2 spaces per indent

            task = Task(
                content=content,
                marker=marker,
                line_number=line_num,
                file_path=file_path,
                indent_level=indent_level
            )

            # Handle hierarchy
            while task_stack and task_stack[-1].indent_level >= indent_level:
                task_stack.pop()

            if task_stack:
                parent = task_stack[-1]
                task.parent = parent
                parent.children.append(task)

            task_stack.append(task)
            tasks.append(task)

        return tasks

    def get_sync_tasks(self, file_path: Path) -> List[Task]:
        """Get only tasks marked for syncing"""
        all_tasks = self.parse_file(file_path)
        return [task for task in all_tasks if task.is_sync_marker]

    def update_task_in_file(self, task: Task, new_marker: str, add_link: Optional[str] = None):
        """Update a task's marker and optionally add TickTick link"""
        with open(task.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Update the marker
        line = lines[task.line_number - 1]
        updated_line = re.sub(r'\[(.)\]', f'[{new_marker}]', line)
        lines[task.line_number - 1] = updated_line

        # Add TickTick link if provided
        if add_link:
            indent = ' ' * (task.indent_level * 2 + 2)
            link_line = f"{indent}[TickTick]({add_link})\n"
            # Check if link already exists
            if task.line_number < len(lines):
                next_line = lines[task.line_number]
                if '[TickTick]' not in next_line:
                    lines.insert(task.line_number, link_line)
            else:
                lines.append(link_line)

        # Write back
        with open(task.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)


if __name__ == '__main__':
    # Test the parser
    vault = Path('/path/to/vault')
    parser = ObsidianParser(vault)

    for file_path in parser.get_files_to_sync():
        tasks = parser.get_sync_tasks(file_path)
        print(f"\n{file_path}:")
        for task in tasks:
            print(f"  - {task.content} (tags: {task.tags})")
