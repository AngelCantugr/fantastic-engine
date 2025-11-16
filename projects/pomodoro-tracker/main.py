#!/usr/bin/env python3
"""
Pomodoro + Time-Boxing Tracker CLI

ADHD-friendly Pomodoro timer with rich CLI output, analytics, and Obsidian integration.
"""
import typer
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import box
from datetime import datetime

from config import get_config
from session_tracker import SessionStore, create_session
from timer import create_timer, format_duration
from analytics import (
    PomodoroAnalytics,
    display_stats,
    display_recent_sessions
)
from obsidian_sync import create_obsidian_sync


app = typer.Typer(
    name="pomodoro",
    help="ADHD-friendly Pomodoro timer with analytics and Obsidian sync",
    add_completion=False
)
console = Console()


def show_welcome() -> None:
    """Show welcome message."""
    welcome = Panel(
        Text.assemble(
            ("🍅 Pomodoro Tracker\n\n", "bold cyan"),
            ("ADHD-friendly time-boxing and focus tracking\n", "yellow"),
            ("Track your focus, build better habits!", "green")
        ),
        border_style="cyan",
        box=box.DOUBLE
    )
    console.print(welcome)


@app.command()
def start(
    topic: Optional[str] = typer.Argument(None, help="What you're working on"),
    duration: int = typer.Option(30, "--duration", "-d", help="Duration in minutes"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    no_sync: bool = typer.Option(False, "--no-sync", help="Don't sync to Obsidian")
):
    """
    Start a Pomodoro session.

    Example:
        pomodoro start "Write documentation" -d 25 -t "writing,docs"
    """
    show_welcome()

    # Get topic if not provided
    if not topic:
        topic = Prompt.ask("[bold cyan]What are you working on?[/bold cyan]")

    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    else:
        tags_input = Prompt.ask(
            "[bold cyan]Tags (comma-separated, or press Enter to skip)[/bold cyan]",
            default=""
        )
        if tags_input:
            tag_list = [tag.strip() for tag in tags_input.split(",")]

    # Create session
    session = create_session(topic=topic, duration_minutes=duration, tags=tag_list)

    # Store session
    store = SessionStore()
    store.add_session(session)

    # Start timer
    timer = create_timer(duration_minutes=duration, topic=topic)
    completed, elapsed_seconds = timer.start()

    # Update session
    if completed or elapsed_seconds > 0:
        console.print()

        # Ask for value rating
        value_rating = IntPrompt.ask(
            "[bold yellow]How valuable was this session? (1-5)[/bold yellow]",
            default=3
        )

        # Clamp value between 1-5
        value_rating = max(1, min(5, value_rating))

        # Optional notes
        notes = Prompt.ask(
            "[bold cyan]Any notes? (or press Enter to skip)[/bold cyan]",
            default=""
        )

        # Complete session
        session.complete(
            actual_duration_seconds=elapsed_seconds,
            value_rating=value_rating,
            notes=notes if notes else None
        )

        store.update_session(session)

        # Show summary
        console.print()
        summary = Panel(
            Text.assemble(
                ("Session Complete!\n\n", "bold green"),
                ("Topic: ", "bold"), (f"{topic}\n", "cyan"),
                ("Duration: ", "bold"), (f"{format_duration(elapsed_seconds)}\n", "green"),
                ("Value Rating: ", "bold"), (f"{'⭐' * value_rating} ({value_rating}/5)\n", "yellow"),
                ("Tags: ", "bold"), (f"{', '.join(tag_list) if tag_list else 'None'}\n", "magenta"),
            ),
            border_style="green",
            box=box.ROUNDED
        )
        console.print(summary)

        # Sync to Obsidian
        if not no_sync:
            obsidian = create_obsidian_sync()
            obsidian.append_session(session)

        # Offer break
        if completed:
            config = get_config()
            take_break = Confirm.ask(
                f"\n[bold yellow]Take a {config.break_duration_minutes}-minute break?[/bold yellow]",
                default=True
            )

            if take_break:
                break_timer = create_timer(
                    duration_minutes=config.break_duration_minutes,
                    topic="Break",
                    is_break=True
                )
                break_timer.start()

                console.print("\n[bold green]Break complete! Ready for another session?[/bold green]\n")


@app.command()
def stats(
    period: str = typer.Argument("week", help="Period: day, week, or month"),
    show_recent: bool = typer.Option(False, "--recent", "-r", help="Show recent sessions")
):
    """
    View statistics and analytics.

    Example:
        pomodoro stats week
        pomodoro stats day --recent
    """
    store = SessionStore()
    analytics = PomodoroAnalytics(store)

    console.print()

    if period == "day":
        stats_data = analytics.get_daily_stats()
        display_stats(stats_data, title="Today's Statistics")
    elif period == "week":
        stats_data = analytics.get_weekly_stats()
        display_stats(stats_data, title="Weekly Statistics")
    elif period == "month":
        stats_data = analytics.get_monthly_stats()
        display_stats(stats_data, title="Monthly Statistics")
    else:
        console.print(f"[red]Unknown period: {period}[/red]")
        console.print("[yellow]Valid periods: day, week, month[/yellow]")
        return

    if show_recent:
        recent_sessions = store.get_recent_sessions(limit=10)
        display_recent_sessions(recent_sessions)

    console.print()


@app.command()
def review(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """
    Generate a weekly review.

    Example:
        pomodoro review
        pomodoro review -o weekly-review.md
    """
    store = SessionStore()
    analytics = PomodoroAnalytics(store)

    console.print("\n[bold cyan]Generating weekly review...[/bold cyan]\n")

    review_text = analytics.generate_weekly_review()

    if output:
        # Save to file
        with open(output, 'w') as f:
            f.write(review_text)
        console.print(f"[green]Review saved to: {output}[/green]\n")
    else:
        # Print to console
        console.print(Panel(
            review_text,
            title="Weekly Review",
            border_style="cyan",
            box=box.ROUNDED
        ))

    console.print()


@app.command()
def recent(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of sessions to show")
):
    """
    Show recent sessions.

    Example:
        pomodoro recent -n 20
    """
    store = SessionStore()
    sessions = store.get_recent_sessions(limit=limit)

    console.print()
    display_recent_sessions(sessions, limit=limit)
    console.print()


@app.command()
def tags():
    """
    List all tags.

    Example:
        pomodoro tags
    """
    store = SessionStore()
    all_tags = store.get_all_tags()

    console.print()

    if not all_tags:
        console.print("[yellow]No tags found[/yellow]")
    else:
        console.print(Panel(
            "\n".join(f"  #{tag}" for tag in all_tags),
            title=f"All Tags ({len(all_tags)})",
            border_style="magenta",
            box=box.ROUNDED
        ))

    console.print()


@app.command()
def sync(
    days: int = typer.Option(7, "--days", "-d", help="Sync sessions from last N days")
):
    """
    Sync sessions to Obsidian.

    Example:
        pomodoro sync --days 7
    """
    store = SessionStore()
    obsidian = create_obsidian_sync()

    if not obsidian.is_configured():
        console.print("\n[red]Obsidian integration not configured![/red]")
        console.print("[yellow]Set OBSIDIAN_VAULT_PATH environment variable[/yellow]\n")
        return

    console.print(f"\n[cyan]Syncing sessions from last {days} days...[/cyan]\n")

    # Get sessions from last N days
    end_date = datetime.now()
    start_date = end_date - __import__('datetime').timedelta(days=days)
    sessions = store.get_sessions_by_date_range(start_date, end_date)

    if not sessions:
        console.print("[yellow]No sessions to sync[/yellow]\n")
        return

    synced = obsidian.sync_multiple_sessions(sessions)
    console.print(f"\n[green]✓ Synced {synced}/{len(sessions)} sessions to Obsidian[/green]\n")


@app.command()
def config_show():
    """
    Show current configuration.

    Example:
        pomodoro config-show
    """
    config = get_config()

    console.print()
    console.print(Panel(
        Text.assemble(
            ("Configuration\n\n", "bold cyan"),
            ("Default Duration: ", "bold"), (f"{config.default_duration_minutes} minutes\n", "green"),
            ("Break Duration: ", "bold"), (f"{config.break_duration_minutes} minutes\n", "green"),
            ("Data Directory: ", "bold"), (f"{config.data_dir}\n", "cyan"),
            ("Sessions File: ", "bold"), (f"{config.sessions_path}\n", "cyan"),
            ("\nObsidian Integration\n", "bold yellow"),
            ("Enabled: ", "bold"), (f"{config.obsidian_enabled}\n", "green" if config.obsidian_enabled else "red"),
            ("Vault Path: ", "bold"), (f"{config.obsidian_vault_path or 'Not set'}\n", "cyan"),
            ("Daily Notes Folder: ", "bold"), (f"{config.obsidian_daily_notes_folder}\n", "cyan"),
        ),
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Pomodoro Tracker - ADHD-friendly time-boxing and focus tracking.
    """
    if ctx.invoked_subcommand is None:
        show_welcome()
        console.print("\n[yellow]Run 'pomodoro --help' to see available commands[/yellow]\n")
        console.print("[cyan]Quick start: pomodoro start \"Your task here\"[/cyan]\n")


if __name__ == "__main__":
    app()
