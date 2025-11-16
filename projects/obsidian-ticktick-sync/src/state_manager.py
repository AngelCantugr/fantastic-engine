"""
Sync state management using SQLite
"""
import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager


class StateManager:
    """Manages sync state in SQLite database"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'sync_state.db')

        self.db_path = Path(db_path)
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    obsidian_path TEXT NOT NULL,
                    obsidian_line_number INTEGER NOT NULL,
                    ticktick_task_id TEXT UNIQUE NOT NULL,
                    task_content TEXT NOT NULL,
                    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified_source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    UNIQUE(obsidian_path, obsidian_line_number)
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    source TEXT NOT NULL,
                    details TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticktick_task_id TEXT NOT NULL,
                    obsidian_path TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0,
                    resolution TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            conn.commit()

    def save_task_state(self, obsidian_path: str, line_number: int,
                       ticktick_task_id: str, content: str,
                       last_modified_source: str, status: str = 'active'):
        """Save or update task sync state"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO sync_state
                (obsidian_path, obsidian_line_number, ticktick_task_id,
                 task_content, last_modified_source, status, last_synced_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (obsidian_path, line_number, ticktick_task_id,
                  content, last_modified_source, status))
            conn.commit()

        self._log_action('save_state', last_modified_source, {
            'task_id': ticktick_task_id,
            'content': content
        })

    def get_task_state(self, obsidian_path: str, line_number: int) -> Optional[Dict]:
        """Get task state by Obsidian location"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM sync_state
                WHERE obsidian_path = ? AND obsidian_line_number = ?
            ''', (obsidian_path, line_number))

            row = cursor.fetchone()
            return dict(row) if row else None

    def get_task_state_by_id(self, ticktick_task_id: str) -> Optional[Dict]:
        """Get task state by TickTick ID"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM sync_state
                WHERE ticktick_task_id = ?
            ''', (ticktick_task_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    def update_task_status(self, ticktick_task_id: str, status: str):
        """Update task status"""
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE sync_state
                SET status = ?, last_synced_at = CURRENT_TIMESTAMP
                WHERE ticktick_task_id = ?
            ''', (status, ticktick_task_id))
            conn.commit()

    def update_task_content(self, ticktick_task_id: str, content: str):
        """Update task content"""
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE sync_state
                SET task_content = ?, last_synced_at = CURRENT_TIMESTAMP
                WHERE ticktick_task_id = ?
            ''', (content, ticktick_task_id))
            conn.commit()

    def get_statistics(self) -> Dict:
        """Get sync statistics"""
        with self._get_connection() as conn:
            # Total tasks
            total = conn.execute('SELECT COUNT(*) FROM sync_state').fetchone()[0]

            # By status
            active = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE status = 'active'"
            ).fetchone()[0]

            completed = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE status = 'completed'"
            ).fetchone()[0]

            cancelled = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE status = 'cancelled'"
            ).fetchone()[0]

            # Last sync
            last_sync = conn.execute(
                'SELECT value FROM metadata WHERE key = "last_sync"'
            ).fetchone()
            last_sync = last_sync[0] if last_sync else 'Never'

            # Conflicts
            conflicts_resolved = conn.execute(
                'SELECT COUNT(*) FROM conflicts WHERE resolved = 1'
            ).fetchone()[0]

        return {
            'total': total,
            'active': active,
            'completed': completed,
            'cancelled': cancelled,
            'last_sync': last_sync,
            'conflicts_resolved': conflicts_resolved
        }

    def get_conflicts(self) -> List[Dict]:
        """Get unresolved conflicts"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT c.*, s.task_content
                FROM conflicts c
                JOIN sync_state s ON c.ticktick_task_id = s.ticktick_task_id
                WHERE c.resolved = 0
                ORDER BY c.created_at DESC
            ''')

            return [dict(row) for row in cursor.fetchall()]

    def log_conflict_resolution(self, ticktick_task_id: str, winner: str, reason: str):
        """Log conflict resolution"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO conflicts
                (ticktick_task_id, obsidian_path, reason, resolved, resolution)
                VALUES (?, ?, ?, 1, ?)
            ''', (ticktick_task_id, '', reason, winner))
            conn.commit()

    def reset_file(self, file_path: str) -> int:
        """Reset sync state for a specific file"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                DELETE FROM sync_state WHERE obsidian_path = ?
            ''', (file_path,))
            conn.commit()
            return cursor.rowcount

    def reset_all(self):
        """Reset all sync state (DANGER!)"""
        with self._get_connection() as conn:
            conn.execute('DELETE FROM sync_state')
            conn.execute('DELETE FROM sync_log')
            conn.execute('DELETE FROM conflicts')
            conn.execute('DELETE FROM metadata')
            conn.commit()

    def update_last_sync(self):
        """Update last sync timestamp"""
        with self._get_connection() as conn:
            now = datetime.now().isoformat()
            conn.execute('''
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES ('last_sync', ?)
            ''', (now,))
            conn.commit()

    def _log_action(self, action: str, source: str, details: Dict):
        """Log an action to sync_log"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO sync_log (action, source, details)
                VALUES (?, ?, ?)
            ''', (action, source, json.dumps(details)))
            conn.commit()


if __name__ == '__main__':
    # Test state manager
    state = StateManager(':memory:')

    # Save a task
    state.save_task_state(
        obsidian_path='/vault/daily/2025-11-16.md',
        line_number=10,
        ticktick_task_id='task123',
        content='Test task',
        last_modified_source='obsidian'
    )

    # Retrieve it
    task = state.get_task_state('/vault/daily/2025-11-16.md', 10)
    print(task)

    # Get stats
    stats = state.get_statistics()
    print(stats)
