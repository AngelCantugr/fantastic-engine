"""
Quick Wins Panel
Displays tasks that take less than 15 minutes.
Perfect for low-energy moments or building momentum with ADHD.
"""

import os
from datetime import datetime
from typing import Dict, List, Any

from rich.panel import Panel
from rich.text import Text


class QuickWinsPanel:
    """
    Panel for displaying quick win tasks (<15 minutes).

    Features:
    - Tasks estimated at <15 minutes
    - Low cognitive load tasks
    - Easy momentum builders
    - Great for low energy moments
    """

    def __init__(self, theme: Dict[str, str], debug: bool = False):
        """
        Initialize the quick wins panel.

        Args:
            theme: Color theme dictionary
            debug: Enable debug logging
        """
        self.theme = theme
        self.debug = debug
        self.quick_wins = []
        self.last_refresh = None

    def refresh(self):
        """Fetch latest quick win tasks."""
        # TODO: Integrate with TickTick MCP to filter tasks by time estimate
        # For now, using mock data
        self.quick_wins = self._fetch_mock_quick_wins()
        self.last_refresh = datetime.now()

    def _fetch_mock_quick_wins(self) -> List[Dict[str, Any]]:
        """
        Fetch mock quick win tasks for development.

        Returns:
            List of quick win task dictionaries
        """
        return [
            {
                "id": "qw1",
                "title": "Update README typo",
                "estimate": 5,
                "tags": ["documentation"],
            },
            {
                "id": "qw2",
                "title": "Respond to email from Sarah",
                "estimate": 10,
                "tags": ["email", "communication"],
            },
            {
                "id": "qw3",
                "title": "Schedule dentist appointment",
                "estimate": 5,
                "tags": ["personal", "health"],
            },
            {
                "id": "qw4",
                "title": "Review quick bug fix PR",
                "estimate": 10,
                "tags": ["code-review"],
            },
            {
                "id": "qw5",
                "title": "Update package.json version",
                "estimate": 3,
                "tags": ["maintenance"],
            },
        ]

    def _get_estimate_display(self, minutes: int) -> str:
        """Format time estimate for display."""
        if minutes == 1:
            return "1 min"
        else:
            return f"{minutes} mins"

    def render(self) -> Panel:
        """
        Render the quick wins panel.

        Returns:
            Rich Panel with quick wins display
        """
        content = Text()

        if not self.quick_wins:
            content.append("🎯 No quick wins available\n\n", style="dim")
            content.append("All tasks require more focus time.", style="italic dim")
        else:
            # Show up to 3 quick wins
            for i, task in enumerate(self.quick_wins[:3], 1):
                # Task title with bullet
                content.append(f"• {task['title']}", style="bold")

                # Time estimate
                estimate_text = self._get_estimate_display(task["estimate"])
                content.append(f" ({estimate_text})", style=self.theme['accent'])
                content.append("\n")

            # Show more indicator
            if len(self.quick_wins) > 3:
                remaining = len(self.quick_wins) - 3
                content.append(
                    f"\n... and {remaining} more quick win{'s' if remaining > 1 else ''}\n",
                    style="dim"
                )

            content.append("\n")

            # Action prompts
            content.append("[t] Mark complete  ", style=f"bold {self.theme['accent']}")
            content.append("[n] Next task", style="dim")

            # Motivation
            content.append("\n\n💡 ", style="dim")
            content.append("Perfect for building momentum!", style="italic dim")

        return Panel(
            content,
            title="🎯 QUICK WINS (<15 MIN)",
            border_style=self.theme["border"],
            padding=(1, 2),
        )
