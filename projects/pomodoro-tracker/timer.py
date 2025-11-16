"""Timer logic with Rich progress bar and visual countdown."""
import time
import sys
from datetime import datetime, timedelta
from typing import Optional, Callable
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TaskProgressColumn
)
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich import box


console = Console()


class PomodoroTimer:
    """A timer for Pomodoro sessions with pause/resume functionality."""

    def __init__(self, duration_minutes: int, topic: str):
        """Initialize the timer."""
        self.duration_minutes = duration_minutes
        self.duration_seconds = duration_minutes * 60
        self.topic = topic
        self.elapsed_seconds = 0
        self.is_paused = False
        self.is_running = False
        self.start_time: Optional[datetime] = None

    def _ring_bell(self) -> None:
        """Ring terminal bell for alert."""
        sys.stdout.write('\a')
        sys.stdout.flush()

    def _create_timer_display(self, remaining_seconds: int, elapsed_seconds: int) -> Table:
        """Create a beautiful timer display."""
        table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")

        # Topic
        topic_text = Text(self.topic, style="bold magenta", justify="center")
        table.add_row("Focus:", topic_text)

        # Time display
        remaining_mins = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
        elapsed_mins = elapsed_seconds // 60
        elapsed_secs = elapsed_seconds % 60

        time_text = Text()
        time_text.append(f"{remaining_mins:02d}:{remaining_secs:02d}", style="bold green")
        time_text.append(" remaining", style="dim")
        table.add_row("Time:", time_text)

        elapsed_text = Text(f"{elapsed_mins:02d}:{elapsed_secs:02d} elapsed", style="dim cyan")
        table.add_row("Elapsed:", elapsed_text)

        # Progress bar
        progress_percent = (elapsed_seconds / self.duration_seconds) * 100
        bar_width = 30
        filled = int((progress_percent / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        progress_text = Text(bar, style="cyan")
        table.add_row("Progress:", progress_text)

        # Status
        status_text = Text("PAUSED", style="bold yellow") if self.is_paused else Text("RUNNING", style="bold green")
        table.add_row("Status:", status_text)

        return table

    def _show_completion_celebration(self, completed: bool) -> None:
        """Show celebration message when timer completes."""
        if completed:
            celebration = Panel(
                Text.assemble(
                    ("🎉 ", "bold yellow"),
                    ("POMODORO COMPLETE!", "bold green"),
                    (" 🎉\n\n", "bold yellow"),
                    ("Great work! Time for a well-deserved break.", "cyan")
                ),
                title="Success!",
                border_style="green",
                box=box.DOUBLE
            )
        else:
            celebration = Panel(
                Text.assemble(
                    ("⏸️ ", "bold yellow"),
                    ("Session Stopped", "bold yellow"),
                    ("\n\n", ""),
                    ("Session ended early.", "cyan")
                ),
                title="Ended",
                border_style="yellow",
                box=box.ROUNDED
            )

        console.print(celebration)
        if completed:
            self._ring_bell()
            time.sleep(0.2)
            self._ring_bell()
            time.sleep(0.2)
            self._ring_bell()

    def start(self, on_tick: Optional[Callable[[int], None]] = None) -> tuple[bool, int]:
        """
        Start the timer with visual display.

        Returns:
            tuple: (completed: bool, elapsed_seconds: int)
        """
        self.is_running = True
        self.start_time = datetime.now()

        console.print()
        console.print(Panel(
            Text.assemble(
                ("🍅 Starting Pomodoro Session\n\n", "bold cyan"),
                ("Topic: ", "bold"), (f"{self.topic}\n", "magenta"),
                ("Duration: ", "bold"), (f"{self.duration_minutes} minutes\n\n", "green"),
                ("Commands:\n", "bold yellow"),
                ("  ", ""), ("Ctrl+C", "bold red"), (" - Stop timer\n", ""),
                ("  ", ""), ("Space", "bold yellow"), (" - Pause/Resume (if implemented in CLI)", "dim")
            ),
            border_style="cyan",
            box=box.DOUBLE
        ))
        console.print()

        try:
            with Live(self._create_timer_display(self.duration_seconds, 0), refresh_per_second=1) as live:
                while self.elapsed_seconds < self.duration_seconds and self.is_running:
                    if not self.is_paused:
                        time.sleep(1)
                        self.elapsed_seconds += 1

                        remaining = self.duration_seconds - self.elapsed_seconds

                        # Update display
                        live.update(self._create_timer_display(remaining, self.elapsed_seconds))

                        # Call callback if provided
                        if on_tick:
                            on_tick(self.elapsed_seconds)

                        # Alert at milestones
                        if remaining in [300, 60, 10]:  # 5 min, 1 min, 10 sec
                            self._ring_bell()
                    else:
                        time.sleep(0.1)  # Small sleep when paused

            completed = self.elapsed_seconds >= self.duration_seconds
            self._show_completion_celebration(completed)

            return completed, self.elapsed_seconds

        except KeyboardInterrupt:
            console.print("\n")
            console.print("[yellow]Timer stopped by user[/yellow]")
            self.is_running = False
            self._show_completion_celebration(False)
            return False, self.elapsed_seconds

    def pause(self) -> None:
        """Pause the timer."""
        self.is_paused = True

    def resume(self) -> None:
        """Resume the timer."""
        self.is_paused = False

    def stop(self) -> None:
        """Stop the timer."""
        self.is_running = False

    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds."""
        return self.elapsed_seconds

    def get_remaining_time(self) -> int:
        """Get remaining time in seconds."""
        return max(0, self.duration_seconds - self.elapsed_seconds)


class BreakTimer(PomodoroTimer):
    """A timer specifically for breaks."""

    def start(self, on_tick: Optional[Callable[[int], None]] = None) -> tuple[bool, int]:
        """Start the break timer."""
        self.is_running = True
        self.start_time = datetime.now()

        console.print()
        console.print(Panel(
            Text.assemble(
                ("☕ Break Time!\n\n", "bold green"),
                ("Duration: ", "bold"), (f"{self.duration_minutes} minutes\n\n", "cyan"),
                ("Relax and recharge!", "yellow")
            ),
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()

        return super().start(on_tick)


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}m {secs}s"


def create_timer(duration_minutes: int, topic: str, is_break: bool = False) -> PomodoroTimer:
    """Create a timer instance."""
    if is_break:
        return BreakTimer(duration_minutes, "Break")
    return PomodoroTimer(duration_minutes, topic)
