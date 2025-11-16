"""
Bidirectional sync engine
"""
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from obsidian_parser import ObsidianParser, Task
from ticktick_client import TickTickClient
from state_manager import StateManager
from conflict_resolver import ConflictResolver


logger = logging.getLogger(__name__)


class SyncEngine:
    """Handles bidirectional synchronization"""

    def __init__(self, parser: ObsidianParser, client: TickTickClient, state: StateManager):
        self.parser = parser
        self.client = client
        self.state = state
        self.resolver = ConflictResolver()

    def sync_all(self, dry_run: bool = False) -> Dict:
        """Sync all files in vault"""
        results = {
            'created': 0,
            'updated': 0,
            'completed': 0,
            'conflicts': 0,
            'errors': 0
        }

        files = self.parser.get_files_to_sync()
        logger.info(f"Syncing {len(files)} files")

        for file_path in files:
            try:
                file_result = self.sync_file(file_path, dry_run)
                for key in results:
                    results[key] += file_result[key]
            except Exception as e:
                logger.error(f"Error syncing {file_path}: {e}")
                results['errors'] += 1

        # Update last sync time
        if not dry_run:
            self.state.update_last_sync()

        return results

    def sync_file(self, file_path: Path, dry_run: bool = False) -> Dict:
        """Sync a single file"""
        results = {
            'created': 0,
            'updated': 0,
            'completed': 0,
            'conflicts': 0,
            'errors': 0
        }

        tasks = self.parser.get_sync_tasks(file_path)
        logger.info(f"Found {len(tasks)} sync tasks in {file_path}")

        for task in tasks:
            try:
                result = self._sync_task(task, dry_run)
                results[result] += 1
            except Exception as e:
                logger.error(f"Error syncing task '{task.content}': {e}")
                results['errors'] += 1

        return results

    def _sync_task(self, task: Task, dry_run: bool = False) -> str:
        """Sync a single task"""
        # Check if task already synced
        sync_state = self.state.get_task_state(
            str(task.file_path),
            task.line_number
        )

        if sync_state is None:
            # New task - create in TickTick
            return self._create_task(task, dry_run)
        else:
            # Existing task - check for updates
            return self._update_task(task, sync_state, dry_run)

    def _create_task(self, task: Task, dry_run: bool = False) -> str:
        """Create new task in TickTick"""
        logger.info(f"Creating new task: {task.content}")

        if dry_run:
            logger.info("[DRY RUN] Would create task in TickTick")
            return 'created'

        # Handle parent task
        parent_id = None
        if task.parent and task.parent.is_sync_marker:
            parent_state = self.state.get_task_state(
                str(task.parent.file_path),
                task.parent.line_number
            )
            if parent_state:
                parent_id = parent_state['ticktick_task_id']

        # Create in TickTick
        ticktick_task = self.client.create_task(
            content=task.content,
            tags=task.tags,
            due_date=task.due_date,
            priority=task.priority,
            parent_id=parent_id
        )

        # Add link back to Obsidian
        task_url = f"https://ticktick.com/task/{ticktick_task['id']}"
        self.parser.update_task_in_file(task, task.marker, add_link=task_url)

        # Save state
        self.state.save_task_state(
            obsidian_path=str(task.file_path),
            line_number=task.line_number,
            ticktick_task_id=ticktick_task['id'],
            content=task.content,
            last_modified_source='obsidian',
            status='active'
        )

        return 'created'

    def _update_task(self, task: Task, sync_state: Dict, dry_run: bool = False) -> str:
        """Update existing task"""
        ticktick_task_id = sync_state['ticktick_task_id']

        # Get current TickTick state
        try:
            ticktick_task = self.client.get_task(ticktick_task_id)
        except Exception as e:
            logger.error(f"Failed to get TickTick task {ticktick_task_id}: {e}")
            return 'errors'

        # Detect changes
        obsidian_modified = task.content != sync_state['task_content']
        ticktick_modified = ticktick_task.get('status') == 'completed' and sync_state['status'] != 'completed'

        # Handle completion
        if task.is_completed and sync_state['status'] != 'completed':
            logger.info(f"Task completed in Obsidian: {task.content}")
            if not dry_run:
                self.client.complete_task(ticktick_task_id)
                self.state.update_task_status(ticktick_task_id, 'completed')
            return 'completed'

        if ticktick_modified and not task.is_completed:
            logger.info(f"Task completed in TickTick: {task.content}")
            if not dry_run:
                self.parser.update_task_in_file(task, 'x')
                self.state.update_task_status(ticktick_task_id, 'completed')
            return 'completed'

        # Handle conflicts
        if obsidian_modified and ticktick_modified:
            logger.warning(f"Conflict detected for task: {task.content}")
            conflict = self.resolver.resolve(
                obsidian_task=task,
                ticktick_task=ticktick_task,
                sync_state=sync_state
            )

            if not dry_run:
                self._apply_conflict_resolution(task, ticktick_task, conflict)

            return 'conflicts'

        # Regular update
        if obsidian_modified:
            logger.info(f"Updating TickTick from Obsidian: {task.content}")
            if not dry_run:
                self.client.update_task(
                    ticktick_task_id,
                    title=task.content,
                    tags=task.tags,
                    due_date=task.due_date
                )
                self.state.update_task_content(ticktick_task_id, task.content)
            return 'updated'

        return 'updated'

    def _apply_conflict_resolution(self, task: Task, ticktick_task: Dict, resolution: Dict):
        """Apply conflict resolution"""
        if resolution['winner'] == 'obsidian':
            # Update TickTick from Obsidian
            self.client.update_task(
                ticktick_task['id'],
                title=task.content,
                tags=task.tags
            )
        else:
            # Update Obsidian from TickTick
            # (This is more complex as it requires rewriting the file)
            pass

        # Log the resolution
        self.state.log_conflict_resolution(
            ticktick_task['id'],
            resolution['winner'],
            resolution['reason']
        )

    def resolve_conflict(self, task_id: str, prefer: str):
        """Manually resolve a conflict"""
        # Implementation for manual conflict resolution
        pass


if __name__ == '__main__':
    # Test sync engine
    from pathlib import Path

    vault = Path('/path/to/vault')
    parser = ObsidianParser(vault)
    client = TickTickClient()
    state = StateManager()

    engine = SyncEngine(parser, client, state)
    result = engine.sync_all(dry_run=True)
    print(result)
