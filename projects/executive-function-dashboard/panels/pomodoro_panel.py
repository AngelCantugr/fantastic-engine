"""
Pomodoro Panel
Displays current Pomodoro session status, time remaining, and session count.
Helps combat time blindness - a common ADHD challenge.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.console import Group


class PomodoroPanel:
    """
    Panel for displaying Pomodoro timer status.

    Features:
    - Current session status (working/break)
    - Time remaining in session
    - Session count for today
    - Visual progress bar
    - Next break countdown
    """

    def __init__(self, theme: Dict[str, str], debug: bool = False):
        """
        Initialize the Pomodoro panel.

        Args:
            theme: Color theme dictionary
            debug: Enable debug logging
        """
        self.theme = theme
        self.debug = debug

        # Load settings from environment
        self.work_minutes = int(os.getenv("POMODORO_WORK_MINUTES", "25"))
        self.break_minutes = int(os.getenv("POMODORO_BREAK_MINUTES", "5"))
        self.long_break_minutes = int(os.getenv("POMODORO_LONG_BREAK_MINUTES", "15"))

        # Session state
        self.session_active = False
        self.session_type = "work"  # "work", "break", "long_break"
        self.session_start = None
        self.session_end = None
        self.sessions_today = 0
        self.last_refresh = None

        # Mock some active state for demo
        self._initialize_mock_session()

    def _initialize_mock_session(self):
        """Initialize a mock active session for demo purposes."""
        self.session_active = True
        self.session_type = "work"
        self.sessions_today = 3
        self.session_start = datetime.now() - timedelta(minutes=6, seconds=28)
        self.session_end = self.session_start + timedelta(minutes=self.work_minutes)

    def refresh(self):
        """Refresh Pomodoro status."""
        # TODO: Integrate with actual Pomodoro tracker
        # For now, just update the timestamp
        self.last_refresh = datetime.now()

    def _get_time_remaining(self) -> Optional[timedelta]:
        """Calculate time remaining in current session."""
        if not self.session_active or not self.session_end:
            return None

        remaining = self.session_end - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def _get_progress_percentage(self) -> float:
        """Calculate progress percentage of current session."""
        if not self.session_active or not self.session_start or not self.session_end:
            return 0.0

        total_duration = (self.session_end - self.session_start).total_seconds()
        elapsed = (datetime.now() - self.session_start).total_seconds()

        if total_duration <= 0:
            return 100.0

        progress = (elapsed / total_duration) * 100
        return min(progress, 100.0)

    def _format_time_remaining(self, td: timedelta) -> str:
        """Format timedelta as MM:SS."""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def render(self) -> Panel:
        """
        Render the Pomodoro panel.

        Returns:
            Rich Panel with Pomodoro status
        """
        content = Text()

        # Session count
        content.append(f"Session {self.sessions_today}/8 today\n\n", style="bold")

        if self.session_active:
            # Status indicator
            if self.session_type == "work":
                content.append("🔴 WORKING\n", style=f"bold {self.theme['danger']}")
            elif self.session_type == "break":
                content.append("🟢 BREAK\n", style=f"bold {self.theme['success']}")
            else:
                content.append("🟡 LONG BREAK\n", style=f"bold {self.theme['warning']}")

            # Time remaining
            time_remaining = self._get_time_remaining()
            if time_remaining:
                formatted_time = self._format_time_remaining(time_remaining)
                content.append(f"⏱️  {formatted_time} remaining\n\n", style=f"bold {self.theme['accent']}")

                # Progress calculation for text display
                progress_pct = self._get_progress_percentage()
                content.append(f"Progress: {progress_pct:.0f}%\n", style="dim")

            # Next action
            if self.session_type == "work":
                content.append("\nNext break in ", style="dim")
                if time_remaining:
                    minutes = int(time_remaining.total_seconds() // 60)
                    content.append(f"{minutes} mins\n", style=self.theme['accent'])
            else:
                content.append("\nBack to work soon\n", style="dim")

            # Controls
            content.append("\n[p] Pause  [s] Skip", style="italic dim")

        else:
            # No active session
            content.append("⏸️  No active session\n\n", style="dim")
            content.append("Ready to focus?\n\n")
            content.append("[p] Start Pomodoro", style=f"bold {self.theme['accent']}")

        return Panel(
            content,
            title="🍅 CURRENT POMODORO",
            border_style=self.theme["border"],
            padding=(1, 2),
        )
