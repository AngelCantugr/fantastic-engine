"""Rich CLI utilities for beautiful terminal UIs."""

from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box


console = Console()


def print_header(title: str, subtitle: Optional[str] = None):
    """Print a cyberpunk-style header."""
    content = f"[bold magenta]{title}[/bold magenta]"
    if subtitle:
        content += f"\n[cyan]{subtitle}[/cyan]"

    console.print(
        Panel(
            content,
            border_style="cyan",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
        )
    )


def print_success(message: str):
    """Print a success message."""
    console.print(f"✅ [green]{message}[/green]")


def print_error(message: str):
    """Print an error message."""
    console.print(f"❌ [red]{message}[/red]")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"⚠️  [yellow]{message}[/yellow]")


def print_info(message: str):
    """Print an info message."""
    console.print(f"ℹ️  [blue]{message}[/blue]")


def print_panel(content: str, title: Optional[str] = None, border_color: str = "cyan"):
    """Print content in a panel."""
    console.print(
        Panel(
            content,
            title=title,
            border_style=border_color,
            padding=(1, 2),
        )
    )


def print_markdown(content: str):
    """Print markdown content."""
    md = Markdown(content)
    console.print(md)


def print_code(code: str, language: str = "python"):
    """Print syntax-highlighted code."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def create_table(
    columns: List[str],
    rows: List[List[str]],
    title: Optional[str] = None
) -> Table:
    """Create a Rich table."""
    table = Table(title=title, border_style="cyan", show_header=True, header_style="bold magenta")

    for column in columns:
        table.add_column(column)

    for row in rows:
        table.add_row(*row)

    return table


def print_table(columns: List[str], rows: List[List[str]], title: Optional[str] = None):
    """Print a table."""
    table = create_table(columns, rows, title)
    console.print(table)


def create_progress() -> Progress:
    """Create a progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )


def print_dict(data: Dict[str, Any], title: Optional[str] = None):
    """Print a dictionary as a formatted table."""
    rows = [[k, str(v)] for k, v in data.items()]
    print_table(["Key", "Value"], rows, title)


def print_list_items(items: List[str], title: Optional[str] = None, numbered: bool = True):
    """Print a list of items."""
    content = []
    for i, item in enumerate(items, 1):
        prefix = f"{i}." if numbered else "•"
        content.append(f"{prefix} {item}")

    if title:
        print_panel("\n".join(content), title=title)
    else:
        for line in content:
            console.print(line)


def prompt_user(question: str, default: Optional[str] = None) -> str:
    """Prompt user for input."""
    if default:
        question = f"{question} [{default}]"
    return console.input(f"[cyan]{question}:[/cyan] ") or default


def confirm(question: str, default: bool = False) -> bool:
    """Ask for yes/no confirmation."""
    default_str = "Y/n" if default else "y/N"
    response = console.input(f"[cyan]{question} [{default_str}]:[/cyan] ").lower()

    if not response:
        return default

    return response in ("y", "yes")


def print_separator():
    """Print a separator line."""
    console.print("─" * console.width, style="dim")
