"""TickTick tasks collector."""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class TickTickCollector:
    """Collects context from TickTick via local MCP server."""

    def __init__(self, mcp_url: str = "http://localhost:3000"):
        self.mcp_url = mcp_url.rstrip('/')
        self._test_connection()

    def _test_connection(self):
        """Test connection to TickTick MCP server."""
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=2)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to TickTick MCP server at {self.mcp_url}. "
                f"Make sure the local server is running. Error: {e}"
            )

    def get_active_tasks(self, limit: int = 20) -> List[Dict]:
        """Get active (incomplete) tasks."""
        try:
            response = requests.get(
                f"{self.mcp_url}/tasks",
                params={"status": "active", "limit": limit},
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("tasks", [])
        except requests.exceptions.RequestException:
            return []

    def get_today_tasks(self) -> List[Dict]:
        """Get tasks due today."""
        try:
            response = requests.get(
                f"{self.mcp_url}/tasks/today",
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("tasks", [])
        except requests.exceptions.RequestException:
            return []

    def get_recent_completed_tasks(self, days: int = 7) -> List[Dict]:
        """Get recently completed tasks."""
        try:
            response = requests.get(
                f"{self.mcp_url}/tasks",
                params={"status": "completed", "days": days},
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("tasks", [])
        except requests.exceptions.RequestException:
            return []

    def summarize_tasks(self, tasks: List[Dict]) -> str:
        """Create a text summary of tasks for AI processing."""
        if not tasks:
            return "No active tasks found."

        summary_parts = ["## Active TickTick Tasks\n"]

        for task in tasks[:15]:  # Limit to 15 tasks
            title = task.get("title", "Untitled")
            priority = task.get("priority", 0)
            tags = task.get("tags", [])
            due_date = task.get("dueDate")

            # Priority indicator
            priority_indicator = ""
            if priority >= 3:
                priority_indicator = "🔴 "
            elif priority == 2:
                priority_indicator = "🟡 "

            # Build task line
            task_line = f"- [ ] {priority_indicator}{title}"

            # Add tags
            if tags:
                task_line += f" {' '.join(f'#{tag}' for tag in tags)}"

            # Add due date
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    task_line += f" 📅 {due.strftime('%Y-%m-%d')}"
                except (ValueError, AttributeError):
                    pass

            summary_parts.append(task_line)

        return "\n".join(summary_parts)
