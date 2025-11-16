"""CLI for CI/CD monitoring daemon."""

import click
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .cicd_monitor import CICDMonitor


console = Console()


@click.command()
@click.option(
    "--daemon",
    is_flag=True,
    help="Run as daemon (continuous monitoring)"
)
@click.option(
    "--once",
    is_flag=True,
    help="Check once and exit"
)
@click.option(
    "--interval",
    type=int,
    default=60,
    help="Poll interval in seconds (daemon mode)"
)
def monitor(daemon: bool, once: bool, interval: int):
    """Monitor GitHub Actions workflows for failures.

    Examples:
        # Start daemon
        python -m src.monitor --daemon

        # Check once
        python -m src.monitor --once

        # Custom interval
        python -m src.monitor --daemon --interval 30
    """
    # TODO: Implement monitoring CLI
    # 1. Load configuration from .env
    # 2. Initialize CICDMonitor
    # 3. If daemon mode:
    #    - Poll continuously
    #    - Display live status table
    # 4. If once mode:
    #    - Check current status
    #    - Exit

    console.print("[cyan]🔍 CI/CD Monitor Agent v0.1.0[/cyan]")

    if daemon:
        console.print(f"[green]🔄 Daemon mode (polling every {interval}s)[/green]")
        console.print("[yellow]⚠️  Daemon not yet implemented[/yellow]")
    elif once:
        console.print("[green]🔍 Checking once...[/green]")
        console.print("[yellow]⚠️  Once mode not yet implemented[/yellow]")
    else:
        console.print("[red]Error:[/red] Use --daemon or --once")


if __name__ == "__main__":
    monitor()
