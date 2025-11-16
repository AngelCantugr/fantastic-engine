"""
Energy Panel
Allows quick energy level check-ins and displays current energy state.
Helps track energy patterns for better task planning with ADHD.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from rich.panel import Panel
from rich.text import Text


class EnergyPanel:
    """
    Panel for energy level tracking and check-ins.

    Features:
    - Current energy level display
    - Quick check-in prompts
    - Last logged timestamp
    - Energy level emoji indicators
    """

    ENERGY_LEVELS = {
        1: {"name": "High", "emoji": "🔋", "description": "Ready to tackle complex tasks"},
        2: {"name": "Medium", "emoji": "⚡", "description": "Good for regular work"},
        3: {"name": "Low", "emoji": "🪫", "description": "Quick wins only"},
        4: {"name": "Depleted", "emoji": "💤", "description": "Time for a break"},
    }

    def __init__(self, theme: Dict[str, str], debug: bool = False):
        """
        Initialize the energy panel.

        Args:
            theme: Color theme dictionary
            debug: Enable debug logging
        """
        self.theme = theme
        self.debug = debug
        self.db_path = Path("data/dashboard.db")
        self.current_energy = None
        self.last_logged = None
        self.last_refresh = None

        # Initialize database
        self._initialize_database()

        # Load current energy level
        self._load_current_energy()

    def _initialize_database(self):
        """Create energy tracking table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS energy_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level INTEGER NOT NULL,
                    notes TEXT
                )
            """)
            conn.commit()

    def _load_current_energy(self):
        """Load the most recent energy log."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT level, timestamp
                FROM energy_logs
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row:
                self.current_energy = row[0]
                self.last_logged = datetime.fromisoformat(row[1])

    def log_energy(self, level: int, notes: Optional[str] = None):
        """
        Log a new energy level.

        Args:
            level: Energy level (1-4)
            notes: Optional notes about the energy level
        """
        if level not in self.ENERGY_LEVELS:
            raise ValueError(f"Invalid energy level: {level}")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO energy_logs (level, notes) VALUES (?, ?)",
                (level, notes)
            )
            conn.commit()

        self.current_energy = level
        self.last_logged = datetime.now()

    def refresh(self):
        """Refresh energy data."""
        self._load_current_energy()
        self.last_refresh = datetime.now()

    def _get_energy_info(self) -> Dict[str, str]:
        """Get information about current energy level."""
        if self.current_energy is None:
            return {
                "name": "Unknown",
                "emoji": "❓",
                "description": "No energy logged yet"
            }
        return self.ENERGY_LEVELS[self.current_energy]

    def _format_last_logged(self) -> str:
        """Format the last logged timestamp."""
        if not self.last_logged:
            return "Never"

        now = datetime.now()
        diff = now - self.last_logged

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min{'s' if minutes > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            return self.last_logged.strftime("%H:%M")

    def render(self) -> Panel:
        """
        Render the energy panel.

        Returns:
            Rich Panel with energy status
        """
        content = Text()

        energy_info = self._get_energy_info()

        # Current energy level
        content.append("Current: ", style="bold")
        content.append(
            f"{energy_info['emoji']} {energy_info['name']}\n",
            style=f"bold {self.theme['accent']}"
        )

        # Description
        content.append(f"{energy_info['description']}\n\n", style="dim")

        # Last logged
        last_logged_str = self._format_last_logged()
        content.append(f"Last logged: {last_logged_str}\n\n", style="dim")

        # Check-in prompt
        content.append("[e] Log energy level\n\n", style=f"bold {self.theme['accent']}")

        # Quick reference
        content.append("Quick reference:\n", style="dim italic")
        content.append("🔋 High  ⚡ Medium  🪫 Low  💤 Depleted", style="dim")

        return Panel(
            content,
            title="⚡ ENERGY CHECK-IN",
            border_style=self.theme["border"],
            padding=(1, 2),
        )
