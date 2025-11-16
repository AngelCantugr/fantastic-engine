"""
Tasks Panel
Displays today's tasks from TickTick via MCP server.
Shows overdue and due-today tasks with priority indicators.
"""

import os
from datetime import datetime
from typing import Dict, List, Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class TasksPanel:
    """
    Panel for displaying today's tasks from TickTick.

    Features:
    - Overdue tasks (red alert)
    - Due today tasks (organized by priority)
    - Priority indicators
    - Task count summaries
    """

    def __init__(self, theme: Dict[str, str], debug: bool = False):
        """
        Initialize the tasks panel.

        Args:
            theme: Color theme dictionary
            debug: Enable debug logging
        """
        self.theme = theme
        self.debug = debug
        self.tasks = []
        self.last_refresh = None

    def refresh(self):
        """Fetch latest tasks from TickTick MCP server."""
        # TODO: Integrate with actual TickTick MCP server
        # For now, using mock data
        self.tasks = self._fetch_mock_tasks()
        self.last_refresh = datetime.now()

    def _fetch_mock_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch mock tasks for development.

        Returns:
            List of task dictionaries
        """
        return [
            {
                "id": "1",
                "title": "Fix login bug",
                "priority": "high",
                "due": "2025-11-15",  # Yesterday
                "overdue": True,
            },
            {
                "id": "2",
                "title": "Review PR #123",
                "priority": "high",
                "due": "2025-11-15",
                "overdue": True,
            },
            {
                "id": "3",
                "title": "Write documentation",
                "priority": "medium",
                "due": "2025-11-16",  # Today
                "overdue": False,
            },
            {
                "id": "4",
                "title": "Team standup",
                "priority": "low",
                "due": "2025-11-16",
                "overdue": False,
            },
            {
                "id": "5",
                "title": "Deploy to staging",
                "priority": "high",
                "due": "2025-11-16",
                "overdue": False,
            },
            {
                "id": "6",
                "title": "Update dependencies",
                "priority": "medium",
                "due": "2025-11-16",
                "overdue": False,
            },
            {
                "id": "7",
                "title": "Code review",
                "priority": "low",
                "due": "2025-11-16",
                "overdue": False,
            },
        ]

    def _get_priority_icon(self, priority: str) -> str:
        """Get icon for task priority."""
        icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
        }
        return icons.get(priority, "⚪")

    def _get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get list of overdue tasks."""
        return [task for task in self.tasks if task.get("overdue", False)]

    def _get_today_tasks(self) -> List[Dict[str, Any]]:
        """Get list of tasks due today."""
        return [task for task in self.tasks if not task.get("overdue", False)]

    def render(self) -> Panel:
        """
        Render the tasks panel.

        Returns:
            Rich Panel with tasks display
        """
        # Create content
        content = Text()

        # Overdue tasks section
        overdue = self._get_overdue_tasks()
        if overdue:
            content.append(f"⚠️  Overdue ({len(overdue)})\n", style=f"bold {self.theme['danger']}")
            for task in overdue[:3]:  # Show max 3 overdue
                priority_icon = self._get_priority_icon(task["priority"])
                content.append(f"{priority_icon} {task['title']}\n", style=self.theme['danger'])
            if len(overdue) > 3:
                content.append(f"   ... and {len(overdue) - 3} more\n", style="dim")
            content.append("\n")

        # Due today section
        today = self._get_today_tasks()
        if today:
            content.append(f"🎯 Due Today ({len(today)})\n", style=f"bold {self.theme['title']}")
            for task in today[:5]:  # Show max 5 today tasks
                priority_icon = self._get_priority_icon(task["priority"])
                content.append(f"{priority_icon} {task['title']}\n")
            if len(today) > 5:
                content.append(f"   ... and {len(today) - 5} more\n", style="dim")
        else:
            content.append("🎉 No tasks due today!\n", style=f"bold {self.theme['success']}")

        # If no tasks at all
        if not self.tasks:
            content = Text("📭 No tasks loaded\n\n", style="dim")
            content.append("Press [r] to refresh", style="italic dim")

        return Panel(
            content,
            title="📋 TODAY'S TASKS",
            border_style=self.theme["border"],
            padding=(1, 2),
        )
