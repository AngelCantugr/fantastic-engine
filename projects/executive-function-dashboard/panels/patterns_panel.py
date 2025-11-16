"""
Patterns Panel
Visualizes focus patterns based on energy logs over time.
Helps identify optimal work times for ADHD productivity.
"""

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from rich.panel import Panel
from rich.text import Text


class PatternsPanel:
    """
    Panel for displaying focus patterns.

    Features:
    - Best focus times based on historical data
    - Energy pattern analysis
    - Recommendations for task scheduling
    - Visual pattern indicators
    """

    def __init__(self, theme: Dict[str, str], debug: bool = False):
        """
        Initialize the patterns panel.

        Args:
            theme: Color theme dictionary
            debug: Enable debug logging
        """
        self.theme = theme
        self.debug = debug
        self.db_path = Path("data/dashboard.db")
        self.patterns = []
        self.best_times = []
        self.pattern_type = None
        self.last_refresh = None

        # Analyze patterns on init
        self._analyze_patterns()

    def _analyze_patterns(self):
        """Analyze energy logs to identify focus patterns."""
        # Get energy logs from last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, level
                FROM energy_logs
                WHERE timestamp >= ?
                ORDER BY timestamp
            """, (seven_days_ago.isoformat(),))

            logs = cursor.fetchall()

        if not logs:
            # Use mock data for demo
            self._generate_mock_patterns()
            return

        # Group by hour of day
        hour_energy = defaultdict(list)

        for timestamp_str, level in logs:
            timestamp = datetime.fromisoformat(timestamp_str)
            hour = timestamp.hour
            hour_energy[hour].append(level)

        # Calculate average energy by hour
        hour_averages = {
            hour: sum(levels) / len(levels)
            for hour, levels in hour_energy.items()
        }

        # Find best focus times (lowest average = highest energy)
        sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1])

        self.best_times = []
        for hour, avg_level in sorted_hours[:3]:  # Top 3 hours
            self.best_times.append({
                "hour": hour,
                "level": self._level_to_name(avg_level),
                "emoji": self._level_to_emoji(avg_level)
            })

        # Determine pattern type
        self._determine_pattern_type(hour_averages)

    def _generate_mock_patterns(self):
        """Generate mock pattern data for demo."""
        self.best_times = [
            {"hour": 9, "level": "High", "emoji": "🔋"},
            {"hour": 14, "level": "Medium", "emoji": "⚡"},
            {"hour": 16, "level": "Low", "emoji": "🪫"},
        ]
        self.pattern_type = "morning_person"

    def _level_to_name(self, avg_level: float) -> str:
        """Convert average level to name."""
        if avg_level <= 1.5:
            return "High"
        elif avg_level <= 2.5:
            return "Medium"
        elif avg_level <= 3.5:
            return "Low"
        else:
            return "Depleted"

    def _level_to_emoji(self, avg_level: float) -> str:
        """Convert average level to emoji."""
        if avg_level <= 1.5:
            return "🔋"
        elif avg_level <= 2.5:
            return "⚡"
        elif avg_level <= 3.5:
            return "🪫"
        else:
            return "💤"

    def _determine_pattern_type(self, hour_averages: Dict[int, float]):
        """Determine overall pattern type (morning person, night owl, etc)."""
        if not hour_averages:
            self.pattern_type = "unknown"
            return

        # Check morning hours (6-12)
        morning_avg = sum(
            level for hour, level in hour_averages.items()
            if 6 <= hour < 12
        ) / max(1, sum(1 for hour in hour_averages if 6 <= hour < 12))

        # Check afternoon hours (12-18)
        afternoon_avg = sum(
            level for hour, level in hour_averages.items()
            if 12 <= hour < 18
        ) / max(1, sum(1 for hour in hour_averages if 12 <= hour < 18))

        # Check evening hours (18-24)
        evening_avg = sum(
            level for hour, level in hour_averages.items()
            if 18 <= hour < 24
        ) / max(1, sum(1 for hour in hour_averages if 18 <= hour < 24))

        # Determine pattern (lower average = better energy)
        if morning_avg < afternoon_avg and morning_avg < evening_avg:
            self.pattern_type = "morning_person"
        elif evening_avg < morning_avg and evening_avg < afternoon_avg:
            self.pattern_type = "night_owl"
        elif afternoon_avg < morning_avg and afternoon_avg < evening_avg:
            self.pattern_type = "afternoon_peak"
        else:
            self.pattern_type = "consistent"

    def _format_time_range(self, hour: int) -> str:
        """Format hour as time range."""
        start = f"{hour:02d}:00"
        end = f"{(hour + 2) % 24:02d}:00"
        period_start = "AM" if hour < 12 else "PM"
        period_end = "AM" if (hour + 2) % 24 < 12 else "PM"

        display_start = hour if hour <= 12 else hour - 12
        display_end = (hour + 2) % 24 if (hour + 2) % 24 <= 12 else (hour + 2) % 24 - 12

        if display_start == 0:
            display_start = 12
        if display_end == 0:
            display_end = 12

        return f"{display_start}:00-{display_end}:00 {period_start}"

    def _get_pattern_recommendation(self) -> str:
        """Get recommendation based on pattern type."""
        recommendations = {
            "morning_person": "Schedule deep work in the morning",
            "night_owl": "Save complex tasks for evening",
            "afternoon_peak": "Peak performance after lunch",
            "consistent": "Steady energy throughout day",
            "unknown": "Log more energy data for insights",
        }
        return recommendations.get(self.pattern_type, "Keep tracking!")

    def refresh(self):
        """Refresh pattern analysis."""
        self._analyze_patterns()
        self.last_refresh = datetime.now()

    def render(self) -> Panel:
        """
        Render the patterns panel.

        Returns:
            Rich Panel with focus patterns
        """
        content = Text()

        if not self.best_times:
            content.append("📊 Not enough data yet\n\n", style="dim")
            content.append("Keep logging your energy levels\n", style="italic")
            content.append("to discover your focus patterns!\n", style="italic")
        else:
            content.append("Best Focus Times:\n\n", style="bold")

            for time_info in self.best_times:
                time_range = self._format_time_range(time_info["hour"])
                content.append(
                    f"{time_info['emoji']} {time_range}  {time_info['level']}\n"
                )

            content.append("\n")

            # Pattern type
            pattern_names = {
                "morning_person": "Morning person",
                "night_owl": "Night owl",
                "afternoon_peak": "Afternoon peak",
                "consistent": "Consistent energy",
                "unknown": "Unknown pattern",
            }

            pattern_name = pattern_names.get(self.pattern_type, "Unknown")
            content.append(f"Pattern: ", style="bold")
            content.append(f"{pattern_name}\n", style=self.theme['accent'])

            # Recommendation
            recommendation = self._get_pattern_recommendation()
            content.append(f"Recommendation: ", style="bold")
            content.append(f"{recommendation}", style=self.theme['success'])

        return Panel(
            content,
            title="📊 FOCUS PATTERNS",
            border_style=self.theme["border"],
            padding=(1, 2),
        )
