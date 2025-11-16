"""
Dashboard Orchestration
Main dashboard logic that coordinates all panels and manages the UI refresh cycle.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from panels.tasks_panel import TasksPanel
from panels.pomodoro_panel import PomodoroPanel
from panels.energy_panel import EnergyPanel
from panels.patterns_panel import PatternsPanel
from panels.quick_wins_panel import QuickWinsPanel


class Dashboard:
    """
    Main dashboard orchestrator.

    Manages the layout, refresh cycle, and coordination between different panels.
    Designed to minimize cognitive load and maximize visibility of important information.
    """

    # Theme color schemes
    THEMES = {
        "cyberpunk": {
            "border": "magenta",
            "title": "cyan",
            "accent": "bright_magenta",
            "success": "bright_green",
            "warning": "bright_yellow",
            "danger": "bright_red",
        },
        "nord": {
            "border": "blue",
            "title": "cyan",
            "accent": "bright_blue",
            "success": "green",
            "warning": "yellow",
            "danger": "red",
        },
        "monokai": {
            "border": "yellow",
            "title": "bright_yellow",
            "accent": "magenta",
            "success": "green",
            "warning": "yellow",
            "danger": "red",
        },
        "dracula": {
            "border": "bright_magenta",
            "title": "bright_cyan",
            "accent": "magenta",
            "success": "bright_green",
            "warning": "bright_yellow",
            "danger": "bright_red",
        },
    }

    def __init__(
        self,
        theme: str = "cyberpunk",
        refresh_interval: int = 300,
        debug: bool = False,
        config_file: Optional[Path] = None,
    ):
        """
        Initialize the dashboard.

        Args:
            theme: Color theme name
            refresh_interval: How often to refresh data (seconds)
            debug: Enable debug logging
            config_file: Optional custom configuration file
        """
        # Load environment variables
        load_dotenv()

        self.theme = self.THEMES.get(theme, self.THEMES["cyberpunk"])
        self.refresh_interval = refresh_interval
        self.debug = debug
        self.console = Console()
        self.running = False

        # Initialize panels
        self.tasks_panel = TasksPanel(theme=self.theme, debug=debug)
        self.pomodoro_panel = PomodoroPanel(theme=self.theme, debug=debug)
        self.energy_panel = EnergyPanel(theme=self.theme, debug=debug)
        self.patterns_panel = PatternsPanel(theme=self.theme, debug=debug)
        self.quick_wins_panel = QuickWinsPanel(theme=self.theme, debug=debug)

        # Create data directory if needed
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Create data directory for local storage if it doesn't exist."""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

    def create_layout(self) -> Layout:
        """
        Create the dashboard layout.

        Returns:
            Rich Layout object with all panels arranged
        """
        # Create main layout
        layout = Layout(name="root")

        # Split into header and body
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=1),
        )

        # Split body into rows
        layout["body"].split_row(
            Layout(name="left_column"),
            Layout(name="right_column"),
        )

        # Split left column
        layout["left_column"].split(
            Layout(name="tasks", ratio=2),
            Layout(name="quick_wins", ratio=1),
        )

        # Split right column
        layout["right_column"].split(
            Layout(name="pomodoro", size=10),
            Layout(name="energy", size=10),
            Layout(name="patterns"),
        )

        return layout

    def create_header(self) -> Panel:
        """Create the dashboard header."""
        title = Text()
        title.append("🧠 ADHD Executive Function Dashboard", style=f"bold {self.theme['title']}")

        subtitle = Text()
        subtitle.append("Your Command Center", style=f"italic {self.theme['accent']}")

        timestamp = Text()
        timestamp.append(
            f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            style="dim"
        )

        header_text = Text.assemble(
            (title, "\n"),
            (subtitle, "\n"),
            timestamp,
        )

        return Panel(
            header_text,
            border_style=self.theme["border"],
            padding=(0, 1),
        )

    def create_footer(self) -> Panel:
        """Create the dashboard footer with keyboard shortcuts."""
        shortcuts = Text()
        shortcuts.append("[q]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Quit  ")
        shortcuts.append("[r]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Refresh  ")
        shortcuts.append("[e]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Log Energy  ")
        shortcuts.append("[p]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Pomodoro  ")
        shortcuts.append("[t]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Complete Task  ")
        shortcuts.append("[?]", style=f"bold {self.theme['accent']}")
        shortcuts.append(" Help")

        return Panel(
            shortcuts,
            border_style=self.theme["border"],
            padding=(0, 1),
        )

    def render_dashboard(self, layout: Layout):
        """
        Render all panels to the layout.

        Args:
            layout: The Rich Layout to populate
        """
        # Update header and footer
        layout["header"].update(self.create_header())
        layout["footer"].update(self.create_footer())

        # Render each panel
        layout["tasks"].update(self.tasks_panel.render())
        layout["pomodoro"].update(self.pomodoro_panel.render())
        layout["energy"].update(self.energy_panel.render())
        layout["patterns"].update(self.patterns_panel.render())
        layout["quick_wins"].update(self.quick_wins_panel.render())

    def refresh_data(self):
        """Refresh data from all panels."""
        if self.debug:
            self.console.log("Refreshing dashboard data...")

        self.tasks_panel.refresh()
        self.pomodoro_panel.refresh()
        self.energy_panel.refresh()
        self.patterns_panel.refresh()
        self.quick_wins_panel.refresh()

    def run(self):
        """
        Run the dashboard with live updates.

        This is the main event loop that keeps the dashboard running and updating.
        """
        self.running = True
        layout = self.create_layout()

        try:
            with Live(
                layout,
                console=self.console,
                screen=True,
                refresh_per_second=1,
            ) as live:
                last_refresh = time.time()

                while self.running:
                    # Check if it's time to refresh
                    current_time = time.time()
                    if current_time - last_refresh >= self.refresh_interval:
                        self.refresh_data()
                        last_refresh = current_time

                    # Render the dashboard
                    self.render_dashboard(layout)

                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)

        except KeyboardInterrupt:
            self.running = False
            raise

    def stop(self):
        """Stop the dashboard."""
        self.running = False
