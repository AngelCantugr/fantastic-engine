"""
TickTick MCP client for fetching tasks
"""
import json
import logging
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class TickTickClient:
    """Client for TickTick MCP Server"""

    def __init__(self, base_url: str = None, config_path: Optional[Path] = None):
        self.base_url = base_url or "http://localhost:3000"
        self.base_url = self.base_url.rstrip('/')
        self.config = self._load_config(config_path)
        self.session = requests.Session()

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load MCP configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'mcp_config.json'

        with open(config_path) as f:
            return json.load(f)

    def get_tasks_for_date(self, target_date: date) -> List[Dict]:
        """Get all tasks for a specific date"""
        logger.info(f"Fetching tasks for {target_date}")

        # Get all tasks
        endpoint = self.config['endpoints']['tasks']
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, timeout=self.config['server']['timeout'])
            response.raise_for_status()
            data = response.json()
            tasks = data.get('tasks', [])

            # Filter for target date
            filtered_tasks = []
            for task in tasks:
                # Check due date
                due_date_str = task.get('dueDate')
                if due_date_str:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                    if due_date == target_date:
                        filtered_tasks.append(task)
                # Also include tasks with no due date if it's today
                elif target_date == datetime.now().date():
                    # Include undated tasks for today only
                    if task.get('status') != 'completed':
                        filtered_tasks.append(task)

            logger.info(f"Found {len(filtered_tasks)} tasks for {target_date}")
            return filtered_tasks

        except requests.RequestException as e:
            logger.error(f"Failed to fetch tasks: {e}")
            raise

    def get_today_tasks(self) -> List[Dict]:
        """Get tasks for today"""
        return self.get_tasks_for_date(datetime.now().date())

    def format_task_for_display(self, task: Dict) -> str:
        """Format task for display in daily note"""
        title = task.get('title', 'Untitled')
        tags = task.get('tags', [])
        priority = task.get('priority', 0)

        # Build task line
        parts = [title]

        # Add tags
        if tags:
            tag_str = ' '.join([f'#{tag}' for tag in tags])
            parts.append(tag_str)

        # Add priority indicator
        if priority > 3:
            parts.append('⭐')

        return ' '.join(parts)


if __name__ == '__main__':
    # Test the client
    client = TickTickClient()

    try:
        tasks = client.get_today_tasks()
        print(f"Found {len(tasks)} tasks for today:")
        for task in tasks:
            print(f"  - {client.format_task_for_display(task)}")
    except Exception as e:
        print(f"Error: {e}")
