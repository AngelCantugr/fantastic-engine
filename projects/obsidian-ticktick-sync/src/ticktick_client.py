"""
TickTick MCP Server client
"""
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

import requests


logger = logging.getLogger(__name__)


class TickTickClient:
    """Client for TickTick MCP Server"""

    def __init__(self, base_url: str = "http://localhost:3000", config_path: Optional[Path] = None):
        self.base_url = base_url.rstrip('/')
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.timeout = self.config['server']['timeout']

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load MCP server configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'mcp_config.json'

        with open(config_path) as f:
            return json.load(f)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to MCP server with retry logic"""
        url = f"{self.base_url}{endpoint}"
        retry_attempts = self.config['server']['retry_attempts']
        retry_delay = self.config['server']['retry_delay']

        for attempt in range(retry_attempts):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt < retry_attempts - 1:
                    logger.warning(f"Request failed, retrying in {retry_delay}s: {e}")
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Request failed after {retry_attempts} attempts: {e}")
                    raise

    def create_task(self, content: str, list_name: str = "Inbox", **kwargs) -> Dict:
        """Create a new task in TickTick"""
        endpoint = self.config['endpoints']['create_task']

        payload = {
            'title': content,
            'list': list_name,
            'priority': kwargs.get('priority', 0),
            'tags': kwargs.get('tags', []),
        }

        if 'due_date' in kwargs:
            payload['dueDate'] = kwargs['due_date']

        if 'description' in kwargs:
            payload['content'] = kwargs['description']

        if 'parent_id' in kwargs:
            payload['parentId'] = kwargs['parent_id']

        logger.info(f"Creating task: {content}")
        result = self._request('POST', endpoint, json=payload)
        return result

    def get_task(self, task_id: str) -> Dict:
        """Get task by ID"""
        endpoint = self.config['endpoints']['task_by_id'].format(task_id=task_id)
        return self._request('GET', endpoint)

    def update_task(self, task_id: str, **kwargs) -> Dict:
        """Update existing task"""
        endpoint = self.config['endpoints']['update_task'].format(task_id=task_id)

        payload = {k: v for k, v in kwargs.items() if v is not None}

        logger.info(f"Updating task {task_id}")
        return self._request('PATCH', endpoint, json=payload)

    def complete_task(self, task_id: str) -> Dict:
        """Mark task as completed"""
        endpoint = self.config['endpoints']['complete_task'].format(task_id=task_id)
        logger.info(f"Completing task {task_id}")
        return self._request('POST', endpoint)

    def delete_task(self, task_id: str) -> Dict:
        """Delete a task"""
        endpoint = self.config['endpoints']['delete_task'].format(task_id=task_id)
        logger.info(f"Deleting task {task_id}")
        return self._request('DELETE', endpoint)

    def get_all_tasks(self, list_name: Optional[str] = None) -> List[Dict]:
        """Get all tasks, optionally filtered by list"""
        endpoint = self.config['endpoints']['tasks']
        params = {}
        if list_name:
            params['list'] = list_name

        result = self._request('GET', endpoint, params=params)
        return result.get('tasks', [])

    def get_lists(self) -> List[Dict]:
        """Get all lists"""
        endpoint = self.config['endpoints']['lists']
        result = self._request('GET', endpoint)
        return result.get('lists', [])

    def check_health(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False


if __name__ == '__main__':
    # Test the client
    client = TickTickClient()

    if client.check_health():
        print("✓ MCP server is healthy")

        # Create a test task
        task = client.create_task(
            "Test task from Python",
            tags=['test'],
            priority=3
        )
        print(f"Created task: {task}")

        # Get the task
        retrieved = client.get_task(task['id'])
        print(f"Retrieved: {retrieved}")

        # Complete it
        client.complete_task(task['id'])
        print("Task completed")
    else:
        print("✗ MCP server is not responding")
