"""Main ultralearning tracker class."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class ProjectMetrics:
    """Metrics for a single project."""
    name: str
    progress_percent: float
    time_hours: float
    velocity: float  # tasks per day
    tasks_completed: int
    tasks_total: int
    status: str  # active, slow, fast, completed
    last_updated: datetime
    file_path: str


@dataclass
class OverallMetrics:
    """Overall metrics across all projects."""
    total_projects: int
    overall_progress: float
    total_hours: float
    this_week_hours: float
    avg_velocity: float
    projects: List[ProjectMetrics]


class UltralearningTracker:
    """Track progress across ultralearning projects."""

    def __init__(
        self,
        projects_root: str,
        include_projects: Optional[List[str]] = None,
        exclude_projects: Optional[List[str]] = None
    ):
        """Initialize tracker.

        Args:
            projects_root: Root directory containing projects
            include_projects: List of project names to include (None = all)
            exclude_projects: List of project names to exclude
        """
        self.projects_root = Path(projects_root)
        self.include_projects = include_projects
        self.exclude_projects = exclude_projects or []
        self.projects = []

    def scan_projects(self) -> List[ProjectMetrics]:
        """Scan projects directory and extract metrics.

        Returns:
            List of ProjectMetrics
        """
        # TODO: Implement project scanning
        # 1. List all directories in projects_root
        # 2. Filter by include/exclude lists
        # 3. For each project:
        #    - Find README.md
        #    - Parse markdown
        #    - Extract metrics
        # 4. Return list of ProjectMetrics

        raise NotImplementedError("Project scanning not yet implemented")

    def get_overall_metrics(self) -> OverallMetrics:
        """Calculate overall metrics.

        Returns:
            OverallMetrics object
        """
        # TODO: Aggregate metrics from all projects
        raise NotImplementedError("Overall metrics not yet implemented")

    def get_project_metrics(self, project_name: str) -> Optional[ProjectMetrics]:
        """Get metrics for specific project.

        Args:
            project_name: Name of project

        Returns:
            ProjectMetrics or None if not found
        """
        # TODO: Return metrics for specific project
        raise NotImplementedError()

    def generate_html_report(self, output_path: str):
        """Generate HTML report with interactive charts.

        Args:
            output_path: Path to output HTML file
        """
        # TODO: Generate HTML report using Plotly + Jinja2
        raise NotImplementedError("HTML report not yet implemented")

    def get_weekly_stats(self) -> Dict:
        """Get statistics for current week.

        Returns:
            Dict with weekly statistics
        """
        # TODO: Calculate weekly stats
        raise NotImplementedError()

    def _parse_project_file(self, file_path: Path) -> ProjectMetrics:
        """Parse project README file.

        Args:
            file_path: Path to README.md

        Returns:
            ProjectMetrics object
        """
        # TODO: Parse markdown and extract:
        # - Progress (checkboxes)
        # - Time spent (time logs)
        # - Last updated
        # - Calculate velocity

        raise NotImplementedError()

    def _calculate_velocity(self, tasks_completed: int, start_date: datetime) -> float:
        """Calculate velocity (tasks per day).

        Args:
            tasks_completed: Number of completed tasks
            start_date: Project start date

        Returns:
            Velocity in tasks/day
        """
        # TODO: Calculate velocity
        raise NotImplementedError()

    def _determine_status(self, velocity: float, avg_velocity: float) -> str:
        """Determine project status.

        Args:
            velocity: Project velocity
            avg_velocity: Average velocity across all projects

        Returns:
            Status string
        """
        # TODO: Determine if project is slow/active/fast
        raise NotImplementedError()
