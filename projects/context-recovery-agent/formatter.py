"""Output formatting for context recovery."""

import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.cli_helpers import (
    console,
    print_header,
    print_panel,
    print_success,
    print_separator
)


class ContextFormatter:
    """Formats context recovery output."""

    @staticmethod
    def print_welcome():
        """Print welcome header."""
        print_header(
            "🧠 Context Recovery Agent",
            "Where you left off..."
        )

    @staticmethod
    def print_analysis_progress(git_count: int, notes_count: int, tasks_count: int):
        """Print analysis progress."""
        console.print("\n📊 Analyzing your digital footprints...")
        print_success(f"Found {git_count} git commits")
        print_success(f"Found {notes_count} recent Obsidian notes")
        print_success(f"Found {tasks_count} active TickTick tasks")
        print_success("Generated context summary")
        print_separator()

    @staticmethod
    def print_context(context: Dict[str, str]):
        """Print the synthesized context."""
        # What you were working on
        if context.get("what_you_were_doing"):
            print_panel(
                context["what_you_were_doing"],
                title="📝 What You Were Working On",
                border_color="magenta"
            )
            print()

        # Next steps
        if context.get("next_steps"):
            print_panel(
                context["next_steps"],
                title="🎯 Next Logical Steps",
                border_color="green"
            )
            print()

        # Blockers and context
        if context.get("blockers"):
            print_panel(
                context["blockers"],
                title="🚧 Blockers & Context",
                border_color="yellow"
            )

    @staticmethod
    def print_no_context():
        """Print message when no context is available."""
        print_panel(
            "No recent activity found. This might be your first time using this tool, "
            "or your activity data is not accessible.\n\n"
            "Try:\n"
            "• Make some git commits\n"
            "• Create notes in Obsidian\n"
            "• Add tasks in TickTick\n\n"
            "Then run this tool again!",
            title="⚠️  No Context Available",
            border_color="yellow"
        )

    @staticmethod
    def print_error(error: str):
        """Print error message."""
        print_panel(
            f"An error occurred:\n\n{error}\n\n"
            "Check your configuration and try again.",
            title="❌ Error",
            border_color="red"
        )
