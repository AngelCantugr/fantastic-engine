#!/usr/bin/env python3
"""
Main entry point for Meeting Notes Processor
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from transcriber import Transcriber
from analyzer import MeetingAnalyzer
from template_engine import TemplateEngine
from obsidian_writer import ObsidianWriter


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
    """Meeting Notes Processor - Turn recordings into structured notes"""
    load_dotenv()
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    ctx.ensure_object(dict)


@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--title', help='Meeting title')
@click.option('--attendees', help='Comma-separated list of attendees')
@click.option('--date', help='Meeting date (YYYY-MM-DD)')
@click.option('--dry-run', is_flag=True, help='Estimate cost without processing')
@click.option('--template', help='Custom template path')
@click.option('--no-transcript', is_flag=True, help='Exclude full transcript from output')
def process(audio_file: str, title: Optional[str], attendees: Optional[str],
           date: Optional[str], dry_run: bool, template: Optional[str],
           no_transcript: bool):
    """Process a meeting recording"""

    audio_path = Path(audio_file)

    # Show file info
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    console.print(f"\n[bold cyan]Processing: {audio_path.name}[/bold cyan]")
    console.print(f"Size: {file_size_mb:.2f} MB")

    # Initialize components
    transcriber = Transcriber()
    analyzer = MeetingAnalyzer()
    template_engine = TemplateEngine(template_path=template)
    obsidian = ObsidianWriter()

    # Estimate cost
    console.print("\n[cyan]Estimating cost...[/cyan]")
    cost_estimate = transcriber.estimate_cost(audio_path)

    console.print(f"Estimated cost: [bold yellow]${cost_estimate['total']:.2f}[/bold yellow]")
    console.print(f"  Transcription: ${cost_estimate['transcription']:.2f}")
    console.print(f"  Analysis: ${cost_estimate['analysis']:.2f}")

    if dry_run:
        console.print("\n[yellow]Dry run complete. No processing performed.[/yellow]")
        return

    # Confirm if cost is high
    warn_threshold = float(os.getenv('WARN_IF_COST_EXCEEDS', 5.0))
    if cost_estimate['total'] > warn_threshold:
        if not click.confirm(f"\nCost exceeds ${warn_threshold}. Continue?"):
            console.print("[yellow]Processing cancelled.[/yellow]")
            return

    # Process with progress indicators
    start_time = datetime.now()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Step 1: Transcribe
        task1 = progress.add_task("[cyan]Transcribing audio...", total=None)
        try:
            transcript_result = transcriber.transcribe(audio_path)
            transcript = transcript_result['text']
            duration = transcript_result.get('duration', 'Unknown')
            progress.update(task1, completed=True)
            console.print(f"[green]✓[/green] Transcription complete ({duration})")
        except Exception as e:
            console.print(f"[red]✗ Transcription failed:[/red] {e}")
            sys.exit(1)

        # Step 2: Analyze
        task2 = progress.add_task("[cyan]Analyzing content...", total=None)
        try:
            analysis = analyzer.analyze(
                transcript=transcript,
                transcript_data=transcript_result
            )
            progress.update(task2, completed=True)
            console.print(f"[green]✓[/green] Analysis complete")
        except Exception as e:
            console.print(f"[red]✗ Analysis failed:[/red] {e}")
            sys.exit(1)

        # Step 3: Render template
        task3 = progress.add_task("[cyan]Generating note...", total=None)
        try:
            # Build context
            context = {
                'meeting_title': title or f"Meeting - {datetime.now().strftime('%Y-%m-%d')}",
                'meeting_date': date or datetime.now().strftime('%Y-%m-%d'),
                'attendees': attendees or analysis.get('attendees', 'Unknown'),
                'duration': duration,
                'meeting_type': analysis.get('meeting_type', 'Meeting'),
                'ai_summary': analysis['summary'],
                'key_outcomes': analysis.get('key_outcomes', ''),
                'action_items': analysis['action_items'],
                'decisions': analysis['decisions'],
                'key_topics': analysis['key_topics'],
                'full_transcript': transcript if not no_transcript else None,
                'timestamps': transcript_result.get('timestamps', []),
                'include_transcript': not no_transcript,
                'processing_stats': True,
                'generation_date': datetime.now().strftime('%Y-%m-%d'),
                'generation_time': datetime.now().strftime('%H:%M:%S'),
                'processing_time': str(datetime.now() - start_time),
                'processing_cost': f"{cost_estimate['total']:.2f}"
            }

            note_content = template_engine.render(context)
            progress.update(task3, completed=True)
            console.print(f"[green]✓[/green] Note generated")
        except Exception as e:
            console.print(f"[red]✗ Note generation failed:[/red] {e}")
            sys.exit(1)

        # Step 4: Save to Obsidian
        task4 = progress.add_task("[cyan]Saving to Obsidian...", total=None)
        try:
            note_path = obsidian.write_note(
                title=context['meeting_title'],
                content=note_content,
                date=context['meeting_date']
            )
            progress.update(task4, completed=True)
            console.print(f"[green]✓[/green] Note saved")
        except Exception as e:
            console.print(f"[red]✗ Save failed:[/red] {e}")
            sys.exit(1)

    # Summary
    total_time = datetime.now() - start_time
    console.print(f"\n[bold green]✓ Processing complete![/bold green]")
    console.print(f"Location: {note_path}")
    console.print(f"Time: {total_time}")
    console.print(f"Cost: ${cost_estimate['total']:.2f}")

    # Show extracted items
    console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Action items: {len(analysis['action_items'].split('- [ ]')) - 1}")
    console.print(f"  Decisions: {len(analysis['decisions'].split('\\n\\n')) if analysis['decisions'] else 0}")
    console.print(f"  Topics: {len(analysis['key_topics'].split('###')) - 1}")


@cli.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('--organize-by-date', is_flag=True, help='Organize output by date')
def batch(folder: str, organize_by_date: bool):
    """Process all recordings in a folder"""
    folder_path = Path(folder)

    # Find all audio files
    audio_files = []
    for ext in ['*.mp3', '*.m4a', '*.wav', '*.webm']:
        audio_files.extend(folder_path.glob(ext))

    if not audio_files:
        console.print("[yellow]No audio files found in folder[/yellow]")
        return

    console.print(f"[cyan]Found {len(audio_files)} audio files[/cyan]\n")

    # Process each
    for i, audio_file in enumerate(audio_files, 1):
        console.print(f"\n[bold]Processing {i}/{len(audio_files)}: {audio_file.name}[/bold]")

        try:
            # Process with default settings
            ctx = click.get_current_context()
            ctx.invoke(process, audio_file=str(audio_file))
        except Exception as e:
            console.print(f"[red]Failed:[/red] {e}")
            continue

    console.print(f"\n[bold green]Batch processing complete![/bold green]")


@cli.command()
def interactive():
    """Interactive mode"""
    console.print("[bold cyan]Meeting Notes Processor - Interactive Mode[/bold cyan]\n")

    # Get audio file
    audio_file = click.prompt("Audio file path")
    if not Path(audio_file).exists():
        console.print("[red]File not found[/red]")
        return

    # Get details
    title = click.prompt("Meeting title", default="")
    attendees = click.prompt("Attendees (comma-separated)", default="")
    date = click.prompt("Meeting date (YYYY-MM-DD)", default=datetime.now().strftime('%Y-%m-%d'))

    # Confirm
    console.print(f"\n[cyan]Ready to process:[/cyan]")
    console.print(f"  File: {audio_file}")
    console.print(f"  Title: {title or '(auto-generated)'}")
    console.print(f"  Date: {date}")

    if click.confirm("\nProcess this recording?", default=True):
        ctx = click.get_current_context()
        ctx.invoke(
            process,
            audio_file=audio_file,
            title=title or None,
            attendees=attendees or None,
            date=date
        )


if __name__ == '__main__':
    cli()
