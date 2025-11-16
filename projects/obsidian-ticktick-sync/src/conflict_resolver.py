"""
Conflict resolution logic
"""
import os
import logging
from typing import Dict
from datetime import datetime

from obsidian_parser import Task


logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolves sync conflicts between Obsidian and TickTick"""

    def __init__(self, strategy: str = None):
        if strategy is None:
            strategy = os.getenv('CONFLICT_STRATEGY', 'last_modified')

        self.strategy = strategy
        logger.info(f"Conflict resolution strategy: {self.strategy}")

    def resolve(self, obsidian_task: Task, ticktick_task: Dict, sync_state: Dict) -> Dict:
        """
        Resolve a conflict between Obsidian and TickTick versions

        Returns:
            Dict with 'winner' and 'reason' keys
        """
        if self.strategy == 'obsidian_wins':
            return {
                'winner': 'obsidian',
                'reason': 'Strategy: Obsidian always wins'
            }

        elif self.strategy == 'ticktick_wins':
            return {
                'winner': 'ticktick',
                'reason': 'Strategy: TickTick always wins'
            }

        elif self.strategy == 'last_modified':
            return self._resolve_by_last_modified(obsidian_task, ticktick_task, sync_state)

        else:
            logger.warning(f"Unknown strategy {self.strategy}, defaulting to last_modified")
            return self._resolve_by_last_modified(obsidian_task, ticktick_task, sync_state)

    def _resolve_by_last_modified(self, obsidian_task: Task, ticktick_task: Dict,
                                  sync_state: Dict) -> Dict:
        """Resolve based on last modification time"""
        # Get last sync time
        last_synced = datetime.fromisoformat(sync_state['last_synced_at'])

        # Get TickTick modification time
        ticktick_modified = datetime.fromisoformat(
            ticktick_task.get('modifiedTime', ticktick_task.get('createdTime'))
        )

        # For Obsidian, we'd need file modification time
        # For now, we'll use a simple heuristic
        obsidian_file = obsidian_task.file_path
        obsidian_modified = datetime.fromtimestamp(obsidian_file.stat().st_mtime)

        # Compare modification times
        if obsidian_modified > ticktick_modified:
            return {
                'winner': 'obsidian',
                'reason': f'Obsidian more recent ({obsidian_modified} vs {ticktick_modified})'
            }
        elif ticktick_modified > obsidian_modified:
            return {
                'winner': 'ticktick',
                'reason': f'TickTick more recent ({ticktick_modified} vs {obsidian_modified})'
            }
        else:
            # Tie - prefer the last known source
            last_source = sync_state.get('last_modified_source', 'obsidian')
            return {
                'winner': last_source,
                'reason': f'Same modification time, preferring last source: {last_source}'
            }

    def can_auto_resolve(self, obsidian_task: Task, ticktick_task: Dict) -> bool:
        """
        Check if conflict can be auto-resolved

        Some conflicts are simple and can be resolved automatically:
        - Status changes only (one side completed)
        - Tag additions (can merge)
        - Priority changes (can pick higher)
        """
        # If only status differs
        obsidian_completed = obsidian_task.is_completed
        ticktick_completed = ticktick_task.get('status') == 'completed'

        if obsidian_completed != ticktick_completed:
            # One side completed, can auto-resolve
            return True

        # Content differs - needs manual resolution
        return False

    def merge_changes(self, obsidian_task: Task, ticktick_task: Dict) -> Dict:
        """
        Attempt to merge non-conflicting changes

        Returns merged task data
        """
        merged = {
            'content': obsidian_task.content,  # Prefer Obsidian content
            'tags': list(set(obsidian_task.tags + ticktick_task.get('tags', []))),
            'priority': max(obsidian_task.priority, ticktick_task.get('priority', 0)),
            'due_date': obsidian_task.due_date or ticktick_task.get('dueDate')
        }

        return merged


if __name__ == '__main__':
    # Test conflict resolver
    resolver = ConflictResolver('last_modified')

    # Simulate a conflict
    from obsidian_parser import Task
    from pathlib import Path

    task = Task(
        content='Test task',
        marker='>',
        line_number=10,
        file_path=Path('/tmp/test.md'),
        indent_level=0
    )

    ticktick_task = {
        'id': 'task123',
        'title': 'Test task (modified)',
        'status': 'active',
        'modifiedTime': '2025-11-16T14:30:00Z'
    }

    sync_state = {
        'last_synced_at': '2025-11-16T14:00:00Z',
        'last_modified_source': 'obsidian'
    }

    resolution = resolver.resolve(task, ticktick_task, sync_state)
    print(resolution)
