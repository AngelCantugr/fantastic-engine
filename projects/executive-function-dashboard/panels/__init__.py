"""
Dashboard Panels Package

Contains all individual panel modules that make up the dashboard.
Each panel is responsible for fetching and displaying specific information.
"""

from .tasks_panel import TasksPanel
from .pomodoro_panel import PomodoroPanel
from .energy_panel import EnergyPanel
from .patterns_panel import PatternsPanel
from .quick_wins_panel import QuickWinsPanel

__all__ = [
    "TasksPanel",
    "PomodoroPanel",
    "EnergyPanel",
    "PatternsPanel",
    "QuickWinsPanel",
]
