"""Analytics and statistics for Pomodoro sessions."""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from session_tracker import PomodoroSession, SessionStore


console = Console()


@dataclass
class SessionStats:
    """Statistics for a set of sessions."""

    total_sessions: int
    completed_sessions: int
    total_minutes: int
    average_value_rating: float
    productive_sessions: int
    unproductive_sessions: int
    most_common_tags: List[Tuple[str, int]]
    best_time_of_day: str
    completion_rate: float


class PomodoroAnalytics:
    """Analytics engine for Pomodoro sessions."""

    def __init__(self, store: SessionStore):
        """Initialize analytics."""
        self.store = store

    def get_weekly_stats(self, date: datetime = None) -> SessionStats:
        """Get statistics for the past week."""
        if date is None:
            date = datetime.now()

        start_date = date - timedelta(days=7)
        sessions = self.store.get_sessions_by_date_range(start_date, date)

        return self._calculate_stats(sessions)

    def get_daily_stats(self, date: datetime = None) -> SessionStats:
        """Get statistics for a specific day."""
        if date is None:
            date = datetime.now()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        sessions = self.store.get_sessions_by_date_range(start_of_day, end_of_day)

        return self._calculate_stats(sessions)

    def get_monthly_stats(self, date: datetime = None) -> SessionStats:
        """Get statistics for the current month."""
        if date is None:
            date = datetime.now()

        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end_of_month = start_of_month.replace(year=date.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=date.month + 1)

        sessions = self.store.get_sessions_by_date_range(start_of_month, end_of_month)

        return self._calculate_stats(sessions)

    def _calculate_stats(self, sessions: List[PomodoroSession]) -> SessionStats:
        """Calculate statistics from a list of sessions."""
        if not sessions:
            return SessionStats(
                total_sessions=0,
                completed_sessions=0,
                total_minutes=0,
                average_value_rating=0.0,
                productive_sessions=0,
                unproductive_sessions=0,
                most_common_tags=[],
                best_time_of_day="N/A",
                completion_rate=0.0
            )

        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.completed)
        total_minutes = sum(s.actual_duration_seconds // 60 if s.actual_duration_seconds else 0 for s in sessions)

        # Value ratings
        rated_sessions = [s for s in sessions if s.value_rating is not None]
        average_value_rating = (
            sum(s.value_rating for s in rated_sessions) / len(rated_sessions)
            if rated_sessions else 0.0
        )

        productive_sessions = sum(1 for s in sessions if s.is_productive)
        unproductive_sessions = sum(1 for s in rated_sessions if not s.is_productive)

        # Tag analysis
        tag_counts = defaultdict(int)
        for session in sessions:
            for tag in session.tags:
                tag_counts[tag] += 1
        most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Time of day analysis
        best_time_of_day = self._find_best_time_of_day(sessions)

        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0

        return SessionStats(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            total_minutes=total_minutes,
            average_value_rating=average_value_rating,
            productive_sessions=productive_sessions,
            unproductive_sessions=unproductive_sessions,
            most_common_tags=most_common_tags,
            best_time_of_day=best_time_of_day,
            completion_rate=completion_rate
        )

    def _find_best_time_of_day(self, sessions: List[PomodoroSession]) -> str:
        """Find the time of day with the highest average value rating."""
        time_periods = {
            "Morning (6-12)": [],
            "Afternoon (12-18)": [],
            "Evening (18-22)": [],
            "Night (22-6)": []
        }

        for session in sessions:
            if session.value_rating is None:
                continue

            hour = session.start_time.hour

            if 6 <= hour < 12:
                time_periods["Morning (6-12)"].append(session.value_rating)
            elif 12 <= hour < 18:
                time_periods["Afternoon (12-18)"].append(session.value_rating)
            elif 18 <= hour < 22:
                time_periods["Evening (18-22)"].append(session.value_rating)
            else:
                time_periods["Night (22-6)"].append(session.value_rating)

        # Find period with highest average
        best_period = "N/A"
        best_avg = 0.0

        for period, ratings in time_periods.items():
            if ratings:
                avg = sum(ratings) / len(ratings)
                if avg > best_avg:
                    best_avg = avg
                    best_period = period

        return best_period if best_avg > 0 else "N/A"

    def get_productivity_patterns(self) -> Dict[str, List[float]]:
        """Analyze productivity patterns by time of day and day of week."""
        all_sessions = self.store.load_sessions()

        # Group by hour of day
        hourly_ratings = defaultdict(list)
        # Group by day of week
        daily_ratings = defaultdict(list)

        for session in all_sessions:
            if session.value_rating is not None:
                hour = session.start_time.hour
                day = session.start_time.strftime("%A")

                hourly_ratings[hour].append(session.value_rating)
                daily_ratings[day].append(session.value_rating)

        return {
            "hourly": dict(hourly_ratings),
            "daily": dict(daily_ratings)
        }

    def generate_weekly_review(self) -> str:
        """Generate a comprehensive weekly review."""
        stats = self.get_weekly_stats()

        review_lines = [
            "# Weekly Pomodoro Review\n",
            f"**Period:** {datetime.now().strftime('%Y-%m-%d')}\n",
            "\n## Summary\n",
            f"- Total Sessions: {stats.total_sessions}",
            f"- Completed: {stats.completed_sessions} ({stats.completion_rate:.1f}%)",
            f"- Total Focus Time: {stats.total_minutes} minutes ({stats.total_minutes/60:.1f} hours)",
            f"- Average Value Rating: {stats.average_value_rating:.1f}/5.0",
            f"- Productive Sessions: {stats.productive_sessions}",
            f"- Best Time of Day: {stats.best_time_of_day}",
            "\n## Top Focus Areas\n"
        ]

        if stats.most_common_tags:
            for tag, count in stats.most_common_tags:
                review_lines.append(f"- {tag}: {count} sessions")
        else:
            review_lines.append("- No tagged sessions this week")

        review_lines.append("\n## Insights\n")

        if stats.average_value_rating >= 4.0:
            review_lines.append("- Excellent week! High value ratings across sessions.")
        elif stats.average_value_rating >= 3.0:
            review_lines.append("- Good week with solid productivity.")
        else:
            review_lines.append("- Consider reviewing your focus areas and time management.")

        if stats.completion_rate >= 80:
            review_lines.append("- Great completion rate! You're building strong focus habits.")
        elif stats.completion_rate >= 50:
            review_lines.append("- Decent completion rate. Try to finish more sessions fully.")
        else:
            review_lines.append("- Low completion rate. Consider shorter sessions or addressing distractions.")

        return "\n".join(review_lines)


def display_stats(stats: SessionStats, title: str = "Statistics") -> None:
    """Display statistics in a beautiful table."""
    table = Table(title=title, box=box.ROUNDED, border_style="cyan", show_header=False)
    table.add_column("Metric", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Total Sessions", str(stats.total_sessions))
    table.add_row("Completed", f"{stats.completed_sessions} ({stats.completion_rate:.1f}%)")
    table.add_row("Total Focus Time", f"{stats.total_minutes} min ({stats.total_minutes/60:.1f} hrs)")
    table.add_row("Avg Value Rating", f"{stats.average_value_rating:.1f}/5.0")
    table.add_row("Productive Sessions", f"{stats.productive_sessions} 🎯")
    table.add_row("Unproductive Sessions", f"{stats.unproductive_sessions}")
    table.add_row("Best Time of Day", stats.best_time_of_day)

    console.print()
    console.print(table)

    if stats.most_common_tags:
        console.print()
        tags_table = Table(title="Top Focus Areas", box=box.SIMPLE, border_style="magenta")
        tags_table.add_column("Tag", style="cyan")
        tags_table.add_column("Count", style="green", justify="right")

        for tag, count in stats.most_common_tags:
            tags_table.add_row(tag, str(count))

        console.print(tags_table)


def display_recent_sessions(sessions: List[PomodoroSession], limit: int = 10) -> None:
    """Display recent sessions in a table."""
    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return

    table = Table(title=f"Recent Sessions (last {limit})", box=box.ROUNDED, border_style="cyan")
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Topic", style="magenta")
    table.add_column("Duration", style="green", justify="right")
    table.add_column("Value", style="yellow", justify="center")
    table.add_column("Status", style="bold")

    for session in sessions[:limit]:
        date_str = session.start_time.strftime("%Y-%m-%d %H:%M")
        value_str = f"{session.value_rating}/5" if session.value_rating else "N/A"
        status = "✓" if session.completed else "✗"
        status_style = "green" if session.completed else "red"

        table.add_row(
            date_str,
            session.topic[:30],
            session.duration_display,
            value_str,
            f"[{status_style}]{status}[/{status_style}]"
        )

    console.print()
    console.print(table)
