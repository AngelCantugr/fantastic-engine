#!/usr/bin/env python3
"""
Context Switch Recovery Assistant CLI
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os

from .snapshot import SnapshotEngine

console = Console()


@click.group()
def main():
    """Context Switch Recovery Assistant"""
    pass


@main.command()
@click.option("--name", "-n", help="Snapshot name")
@click.option("--no-ai", is_flag=True, help="Skip AI summary")
@click.argument("path", default=".")
def snapshot(path: str, name: str = None, no_ai: bool = False):
    """Create a snapshot of current workspace"""
    engine = SnapshotEngine()

    with console.status("[bold green]Creating snapshot..."):
        snap = engine.create_snapshot(
            project_path=path,
            name=name,
            include_ai_summary=not no_ai,
        )

    console.print(f"\n[green]✅ Snapshot created: {snap.name}[/green]")
    console.print(f"ID: {snap.id}")
    console.print(f"Project: {snap.project_path}")
    console.print(f"Branch: {snap.git_branch}")

    if snap.ai_summary:
        console.print(Panel(snap.ai_summary, title="AI Summary", border_style="cyan"))


@main.command()
@click.option("--project", "-p", help="Filter by project path")
@click.option("--limit", "-l", default=10, type=int)
def list(project: str = None, limit: int = 10):
    """List snapshots"""
    engine = SnapshotEngine()
    snapshots = engine.list_snapshots(project_path=project, limit=limit)

    if not snapshots:
        console.print("[yellow]No snapshots found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Timestamp")
    table.add_column("Branch")
    table.add_column("Project")

    for snap in snapshots:
        table.add_row(
            str(snap.id),
            snap.name or "Unnamed",
            snap.timestamp.strftime("%Y-%m-%d %H:%M"),
            snap.git_branch or "N/A",
            snap.project_path,
        )

    console.print(table)


@main.command()
@click.argument("snapshot_id", type=int)
def show(snapshot_id: int):
    """Show snapshot details"""
    engine = SnapshotEngine()
    snap = engine.get_snapshot(snapshot_id)

    if not snap:
        console.print(f"[red]Snapshot {snapshot_id} not found[/red]")
        return

    console.print(f"\n[bold cyan]Snapshot #{snap.id}: {snap.name}[/bold cyan]\n")

    info_table = Table(show_header=False)
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")

    info_table.add_row("Timestamp", snap.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    info_table.add_row("Project", snap.project_path)
    info_table.add_row("Git Branch", snap.git_branch or "N/A")
    info_table.add_row("Git Commit", snap.git_commit[:8] if snap.git_commit else "N/A")

    console.print(info_table)

    if snap.ai_summary:
        console.print("\n")
        console.print(Panel(snap.ai_summary, title="What You Were Working On", border_style="green"))

    if snap.editor_state:
        console.print(f"\n[bold]Editor State:[/bold] {len(snap.editor_state)} items")

    if snap.terminal_state:
        console.print("\n[bold]Terminal:[/bold]")
        if "cwd" in snap.terminal_state:
            console.print(f"  CWD: {snap.terminal_state['cwd']}")
        if "history" in snap.terminal_state and snap.terminal_state["history"]:
            console.print("  Recent commands:")
            for cmd in snap.terminal_state["history"][-5:]:
                console.print(f"    $ {cmd}")


@main.command()
@click.argument("snapshot_id", type=int)
@click.option("--git", is_flag=True, help="Restore git state")
@click.option("--terminal", is_flag=True, help="Restore terminal state")
@click.option("--all", "restore_all", is_flag=True, help="Restore everything")
def restore(snapshot_id: int, git: bool, terminal: bool, restore_all: bool):
    """Restore workspace from snapshot"""
    engine = SnapshotEngine()

    components = []
    if restore_all:
        components = ["git", "editor", "terminal", "env"]
    else:
        if git:
            components.append("git")
        if terminal:
            components.append("terminal")

    if not components:
        console.print("[yellow]No components specified. Use --git, --terminal, or --all[/yellow]")
        return

    with console.status("[bold green]Restoring snapshot..."):
        results = engine.restore_snapshot(snapshot_id, components)

    console.print("\n[bold]Restore Results:[/bold]\n")

    for component, success in results.items():
        status = "✅" if success else "❌"
        console.print(f"  {status} {component}")


@main.command()
@click.argument("snapshot_id", type=int)
def delete(snapshot_id: int):
    """Delete a snapshot"""
    engine = SnapshotEngine()

    if click.confirm(f"Delete snapshot {snapshot_id}?"):
        engine.delete_snapshot(snapshot_id)
        console.print(f"[green]✅ Snapshot {snapshot_id} deleted[/green]")


@main.command()
def monitor():
    """Start background monitoring (auto-snapshot every 15 min)"""
    import time

    engine = SnapshotEngine()
    cwd = os.getcwd()

    console.print("[cyan]🔍 Context Monitor started[/cyan]")
    console.print(f"Monitoring: {cwd}")
    console.print("Auto-snapshot every 15 minutes")
    console.print("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(15 * 60)  # 15 minutes

            console.print(f"[dim]{time.strftime('%H:%M')} - Creating auto-snapshot...[/dim]")
            snap = engine.create_snapshot(cwd, include_ai_summary=False)
            console.print(f"[dim]  → Snapshot #{snap.id} created[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")


if __name__ == "__main__":
    main()
