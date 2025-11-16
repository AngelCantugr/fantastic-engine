#!/usr/bin/env python3
"""
Main entry point for Obsidian-TickTick sync
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from obsidian_parser import ObsidianParser
from ticktick_client import TickTickClient
from sync_engine import SyncEngine
from state_manager import StateManager


# Setup rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
@click.pass_context
def cli(ctx, log_level):
    """Obsidian-TickTick Sync Tool"""
    load_dotenv()
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    ctx.ensure_object(dict)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be synced without making changes')
@click.option('--file', help='Sync specific file only')
def sync_once(dry_run: bool, file: Optional[str]):
    """Run sync once and exit"""
    console.print("[bold cyan]Starting one-time sync...[/bold cyan]")

    vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH'))
    mcp_url = os.getenv('TICKTICK_MCP_URL', 'http://localhost:3000')

    # Initialize components
    parser = ObsidianParser(vault_path)
    client = TickTickClient(mcp_url)
    state = StateManager()
    engine = SyncEngine(parser, client, state)

    # Run sync
    try:
        if file:
            result = engine.sync_file(Path(file), dry_run=dry_run)
        else:
            result = engine.sync_all(dry_run=dry_run)

        # Display results
        console.print(f"\n[bold green]Sync completed![/bold green]")
        console.print(f"Created: {result['created']}")
        console.print(f"Updated: {result['updated']}")
        console.print(f"Completed: {result['completed']}")
        console.print(f"Conflicts: {result['conflicts']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Sync failed")
        sys.exit(1)


@cli.command()
@click.option('--interval', type=int, help='Override sync interval (seconds)')
def daemon(interval: Optional[int]):
    """Run sync continuously as daemon"""
    console.print("[bold cyan]Starting sync daemon...[/bold cyan]")

    vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH'))
    mcp_url = os.getenv('TICKTICK_MCP_URL', 'http://localhost:3000')
    sync_interval = interval or int(os.getenv('SYNC_INTERVAL_SECONDS', 300))

    # Initialize components
    parser = ObsidianParser(vault_path)
    client = TickTickClient(mcp_url)
    state = StateManager()
    engine = SyncEngine(parser, client, state)

    console.print(f"Syncing every {sync_interval} seconds")
    console.print("Press Ctrl+C to stop\n")

    try:
        while True:
            try:
                result = engine.sync_all()
                logger.info(
                    f"Sync: +{result['created']} ~{result['updated']} "
                    f"✓{result['completed']} ⚠{result['conflicts']}"
                )
            except Exception as e:
                logger.error(f"Sync failed: {e}")

            time.sleep(sync_interval)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Stopping sync daemon...[/bold yellow]")


@cli.command()
def stats():
    """Show sync statistics"""
    state = StateManager()
    stats = state.get_statistics()

    console.print("\n[bold cyan]Sync Statistics[/bold cyan]")
    console.print(f"Total synced tasks: {stats['total']}")
    console.print(f"Active: {stats['active']}")
    console.print(f"Completed: {stats['completed']}")
    console.print(f"Cancelled: {stats['cancelled']}")
    console.print(f"Last sync: {stats['last_sync']}")
    console.print(f"Conflicts resolved: {stats['conflicts_resolved']}")


@cli.command()
def show_conflicts():
    """Show unresolved conflicts"""
    state = StateManager()
    conflicts = state.get_conflicts()

    if not conflicts:
        console.print("[green]No conflicts![/green]")
        return

    console.print(f"\n[bold yellow]Found {len(conflicts)} conflicts[/bold yellow]\n")
    for conflict in conflicts:
        console.print(f"Task: {conflict['content']}")
        console.print(f"  Obsidian: {conflict['obsidian_path']}")
        console.print(f"  TickTick: {conflict['ticktick_id']}")
        console.print(f"  Reason: {conflict['reason']}\n")


@cli.command()
@click.argument('task_id')
@click.option('--prefer', type=click.Choice(['obsidian', 'ticktick']), required=True)
def resolve_conflict(task_id: str, prefer: str):
    """Resolve a specific conflict"""
    state = StateManager()
    engine = SyncEngine(None, None, state)

    try:
        engine.resolve_conflict(task_id, prefer)
        console.print(f"[green]Conflict resolved, preferring {prefer}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('file_path')
def reset_file(file_path: str):
    """Reset sync state for a specific file"""
    state = StateManager()
    count = state.reset_file(file_path)
    console.print(f"[green]Reset {count} tasks from {file_path}[/green]")


@cli.command()
@click.option('--confirm', is_flag=True, help='Confirm you want to reset everything')
def reset_all(confirm: bool):
    """Reset all sync state (DANGER!)"""
    if not confirm:
        console.print("[yellow]Add --confirm to reset all sync state[/yellow]")
        return

    state = StateManager()
    state.reset_all()
    console.print("[green]All sync state reset[/green]")


if __name__ == '__main__':
    cli()
