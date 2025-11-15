#!/usr/bin/env python3
"""
LLM Cost Optimizer CLI
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from .tracker import CostTracker, APICall, PromptCache

console = Console()


@click.group()
def main():
    """LLM Cost Optimizer - Track and optimize AI costs"""
    pass


@main.command()
@click.option("--project", "-p", required=True, help="Project name")
@click.option("--model", "-m", required=True, help="Model name")
@click.option("--prompt-tokens", type=int, required=True)
@click.option("--completion-tokens", type=int, required=True)
def track(project: str, model: str, prompt_tokens: int, completion_tokens: int):
    """Manually track an API call"""
    tracker = CostTracker(project)
    tracker.record_call(model, "completion", prompt_tokens, completion_tokens)

    cost = tracker.calculate_cost(model, prompt_tokens, completion_tokens)
    console.print(f"[green]✅ Tracked API call[/green]")
    console.print(f"Cost: ${cost:.4f}")


@main.command()
@click.option("--project", "-p", help="Filter by project")
def stats(project: str = None):
    """Show cost statistics"""
    if project:
        tracker = CostTracker(project)
        stats = tracker.get_project_stats()

        # Display project stats
        console.print(f"\n[bold cyan]📊 Stats for {project}[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric")
        table.add_column("Value", justify="right")

        table.add_row("Total Cost", f"${stats['total_cost']:.2f}")
        table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
        table.add_row("Total Calls", f"{stats['total_calls']:,}")
        table.add_row("Cached Calls", f"{stats['cached_calls']:,}")
        table.add_row("Cache Hit Rate", f"{stats['cache_hit_rate']:.1f}%")

        console.print(table)

        # Model breakdown
        if stats["models"]:
            console.print("\n[bold]Model Breakdown:[/bold]\n")

            model_table = Table(show_header=True, header_style="bold yellow")
            model_table.add_column("Model")
            model_table.add_column("Calls", justify="right")
            model_table.add_column("Tokens", justify="right")
            model_table.add_column("Cost", justify="right")

            for model, data in stats["models"].items():
                model_table.add_row(
                    model,
                    f"{data['calls']:,}",
                    f"{data['tokens']:,}",
                    f"${data['cost']:.2f}",
                )

            console.print(model_table)

        # Optimization suggestions
        suggestions = tracker.get_optimization_suggestions()
        if suggestions:
            console.print("\n[bold green]💡 Optimization Suggestions:[/bold green]\n")
            for suggestion in suggestions:
                console.print(f"  {suggestion}")

    else:
        # Show all projects
        engine = create_engine("sqlite:///./llm_costs.db")
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        projects = session.query(
            APICall.project,
            func.sum(APICall.cost).label("total_cost"),
            func.sum(APICall.total_tokens).label("total_tokens"),
            func.count(APICall.id).label("total_calls"),
        ).group_by(APICall.project).all()

        console.print("\n[bold cyan]📊 All Projects[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Project")
        table.add_column("Calls", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")

        for project_data in projects:
            table.add_row(
                project_data.project,
                f"{project_data.total_calls:,}",
                f"{project_data.total_tokens:,}",
                f"${project_data.total_cost:.2f}",
            )

        console.print(table)


@main.command()
@click.option("--project", "-p", required=True)
def suggest(project: str):
    """Get optimization suggestions"""
    tracker = CostTracker(project)
    suggestions = tracker.get_optimization_suggestions()

    console.print(f"\n[bold green]💡 Optimization Suggestions for {project}[/bold green]\n")

    if suggestions:
        for suggestion in suggestions:
            console.print(Panel(suggestion, border_style="green"))
    else:
        console.print("[green]✅ Your usage is already optimized![/green]")


@main.command()
def cache_stats():
    """Show cache statistics"""
    engine = create_engine("sqlite:///./llm_costs.db")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    caches = session.query(PromptCache).order_by(PromptCache.hits.desc()).limit(10).all()

    console.print("\n[bold cyan]💾 Top Cached Prompts[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model")
    table.add_column("Hits", justify="right")
    table.add_column("Last Used")
    table.add_column("Prompt Preview")

    for cache in caches:
        preview = cache.prompt[:50] + "..." if len(cache.prompt) > 50 else cache.prompt
        table.add_row(
            cache.model,
            str(cache.hits),
            cache.last_used.strftime("%Y-%m-%d %H:%M"),
            preview,
        )

    console.print(table)


@main.command()
@click.option("--project", "-p", required=True)
@click.option("--days", "-d", default=30, type=int)
def export(project: str, days: int):
    """Export cost data to CSV"""
    import pandas as pd

    engine = create_engine("sqlite:///./llm_costs.db")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    cutoff = datetime.utcnow() - timedelta(days=days)
    calls = session.query(APICall).filter(
        APICall.project == project,
        APICall.timestamp >= cutoff
    ).all()

    data = []
    for call in calls:
        data.append({
            "timestamp": call.timestamp,
            "model": call.model,
            "operation": call.operation,
            "prompt_tokens": call.prompt_tokens,
            "completion_tokens": call.completion_tokens,
            "total_tokens": call.total_tokens,
            "cost": call.cost,
            "cached": bool(call.cached),
        })

    df = pd.DataFrame(data)
    filename = f"{project}_costs_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False)

    console.print(f"[green]✅ Exported to {filename}[/green]")


if __name__ == "__main__":
    main()
