#!/usr/bin/env python3
"""
Main entry point for Daily Note Generator
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from ticktick_client import TickTickClient
from obsidian_manager import ObsidianManager
from context_builder import ContextBuilder
from ai_generator import AIGenerator
from template_engine import TemplateEngine


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
    """Daily Note Generator - AI-powered daily planning"""
    load_dotenv()
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    ctx.ensure_object(dict)


@cli.command()
@click.option('--date', help='Date for note (YYYY-MM-DD), defaults to today')
@click.option('--dry-run', is_flag=True, help='Preview without creating file')
@click.option('--template', help='Custom template path')
@click.option('--force', is_flag=True, help='Overwrite existing note')
def generate(date: Optional[str], dry_run: bool, template: Optional[str], force: bool):
    """Generate daily note"""
    # Parse date
    if date:
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
            sys.exit(1)
    else:
        target_date = datetime.now().date()

    console.print(f"[bold cyan]Generating daily note for {target_date}...[/bold cyan]\n")

    # Initialize components
    vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH'))
    ticktick = TickTickClient()
    obsidian = ObsidianManager(vault_path)
    context_builder = ContextBuilder()
    ai = AIGenerator()
    template_engine = TemplateEngine(template_path=template)

    try:
        # Step 1: Check if note already exists
        if obsidian.note_exists(target_date) and not force:
            console.print(f"[yellow]Note for {target_date} already exists. Use --force to overwrite.[/yellow]")
            sys.exit(0)

        # Step 2: Get yesterday's note
        yesterday = target_date - timedelta(days=1)
        yesterday_note = obsidian.read_note(yesterday)

        if yesterday_note:
            console.print(f"[green]✓[/green] Found yesterday's note ({yesterday})")
        else:
            console.print(f"[yellow]ℹ[/yellow] No note found for yesterday ({yesterday})")

        # Step 3: Get today's tasks
        console.print(f"[cyan]Fetching tasks from TickTick...[/cyan]")
        tasks = ticktick.get_tasks_for_date(target_date)
        console.print(f"[green]✓[/green] Found {len(tasks)} tasks")

        # Step 4: Build context
        console.print(f"[cyan]Building context...[/cyan]")
        context = context_builder.build(
            yesterday_note=yesterday_note,
            today_tasks=tasks,
            target_date=target_date
        )

        # Step 5: Generate AI insights
        console.print(f"[cyan]Generating AI insights...[/cyan]")
        ai_summary = ai.generate_summary(context)
        priority_tasks = ai.suggest_priorities(context, tasks)

        console.print(f"[green]✓[/green] AI insights generated")

        # Step 6: Render template
        console.print(f"[cyan]Rendering template...[/cyan]")
        note_content = template_engine.render(
            date=target_date,
            ai_summary=ai_summary,
            priority_tasks=priority_tasks,
            all_tasks=tasks,
            context=context
        )

        # Step 7: Preview or save
        if dry_run:
            console.print("\n[bold yellow]DRY RUN - Preview:[/bold yellow]\n")
            console.print(note_content)
            console.print("\n[yellow]Note not saved (dry run mode)[/yellow]")
        else:
            obsidian.write_note(target_date, note_content)
            note_path = obsidian.get_note_path(target_date)
            console.print(f"\n[bold green]✓ Daily note created![/bold green]")
            console.print(f"Location: {note_path}")

        # Display summary
        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Tasks: {len(tasks)}")
        console.print(f"  Priorities: {len(priority_tasks)}")
        console.print(f"  Had yesterday's context: {'Yes' if yesterday_note else 'No'}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Generation failed")
        sys.exit(1)


@cli.command()
@click.option('--interactive', is_flag=True, help='Interactive mode')
def interactive(interactive):
    """Interactive daily note generation"""
    console.print("[bold cyan]Interactive Daily Note Generator[/bold cyan]\n")

    # Ask for date
    use_today = click.confirm("Generate note for today?", default=True)
    if use_today:
        target_date = datetime.now().date()
    else:
        date_str = click.prompt("Enter date (YYYY-MM-DD)")
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Ask for template
    use_default_template = click.confirm("Use default template?", default=True)
    template = None if use_default_template else click.prompt("Template path")

    # Ask for customization
    customize = click.confirm("Customize priorities?", default=False)

    # Generate with options
    ctx = click.get_current_context()
    ctx.invoke(generate, date=str(target_date), template=template, dry_run=True)

    if customize:
        console.print("\n[yellow]Priority customization not yet implemented[/yellow]")

    # Confirm and save
    if click.confirm("Create this note?", default=True):
        ctx.invoke(generate, date=str(target_date), template=template, force=True)


@cli.command()
def show_tasks():
    """Show today's tasks from TickTick"""
    console.print("[bold cyan]Today's Tasks[/bold cyan]\n")

    ticktick = TickTickClient()
    tasks = ticktick.get_tasks_for_date(datetime.now().date())

    if not tasks:
        console.print("[yellow]No tasks for today[/yellow]")
        return

    for i, task in enumerate(tasks, 1):
        priority = "🔴" if task.get('priority', 0) > 3 else "🔵"
        tags = " ".join([f"#{tag}" for tag in task.get('tags', [])])
        console.print(f"{i}. {priority} {task['title']} {tags}")


@cli.command()
@click.argument('template_path')
def validate_template(template_path: str):
    """Validate a template file"""
    console.print(f"[cyan]Validating template: {template_path}[/cyan]\n")

    try:
        engine = TemplateEngine(template_path=template_path)
        engine.validate()
        console.print("[green]✓ Template is valid[/green]")
    except Exception as e:
        console.print(f"[red]✗ Template validation failed:[/red] {e}")
        sys.exit(1)


@cli.command()
def weekly_review():
    """Generate weekly review (Sunday summary)"""
    console.print("[bold cyan]Weekly Review[/bold cyan]\n")
    console.print("[yellow]Not yet implemented[/yellow]")


if __name__ == '__main__':
    cli()
