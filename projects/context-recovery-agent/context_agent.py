"""Core context recovery agent."""

from pathlib import Path
from typing import Dict, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors import GitCollector, ObsidianCollector, TickTickCollector
from synthesizer import ContextSynthesizer
from formatter import ContextFormatter


class ContextRecoveryAgent:
    """Main agent for context recovery."""

    def __init__(
        self,
        repo_path: Optional[Path] = None,
        vault_path: Optional[Path] = None,
        ticktick_url: str = "http://localhost:3000",
        ai_provider: str = "openai",
        ai_model: Optional[str] = None
    ):
        # Set defaults
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

        # Initialize collectors
        self.git = self._init_git_collector()
        self.obsidian = self._init_obsidian_collector(vault_path)
        self.ticktick = self._init_ticktick_collector(ticktick_url)

        # Initialize synthesizer
        self.synthesizer = ContextSynthesizer(
            provider=ai_provider,
            model=ai_model,
            fallback_to_ollama=True
        )

        # Initialize formatter
        self.formatter = ContextFormatter()

    def _init_git_collector(self) -> Optional[GitCollector]:
        """Initialize git collector."""
        try:
            return GitCollector(self.repo_path)
        except ValueError as e:
            print(f"⚠️  Git: {e}")
            return None

    def _init_obsidian_collector(self, vault_path: Optional[Path]) -> Optional[ObsidianCollector]:
        """Initialize Obsidian collector."""
        try:
            return ObsidianCollector(vault_path)
        except (ValueError, ImportError) as e:
            print(f"⚠️  Obsidian: Could not initialize ({e})")
            return None

    def _init_ticktick_collector(self, url: str) -> Optional[TickTickCollector]:
        """Initialize TickTick collector."""
        try:
            return TickTickCollector(url)
        except ConnectionError as e:
            print(f"⚠️  TickTick: {e}")
            return None

    def recover_context(self, commit_count: int = 3, note_days: int = 1) -> Dict[str, str]:
        """
        Recover context from all sources.

        Args:
            commit_count: Number of recent commits to analyze
            note_days: Number of days of notes to include

        Returns:
            Dictionary with synthesized context
        """
        # Collect data from all sources
        git_summary, git_count, branch_info = self._collect_git_context(commit_count)
        obsidian_summary, notes_count = self._collect_obsidian_context(note_days)
        ticktick_summary, tasks_count = self._collect_ticktick_context()

        # Check if we have any context
        if git_count == 0 and notes_count == 0 and tasks_count == 0:
            return {}

        # Synthesize context
        context = self.synthesizer.synthesize_context(
            git_summary=git_summary,
            obsidian_summary=obsidian_summary,
            ticktick_summary=ticktick_summary,
            branch_info=branch_info
        )

        return context

    def _collect_git_context(self, count: int) -> tuple[str, int, Dict]:
        """Collect git context."""
        if not self.git:
            return "No git repository found.", 0, {}

        try:
            commits = self.git.get_recent_commits(count)
            branch_info = self.git.get_branch_info()

            if not commits:
                return "No recent commits.", 0, branch_info

            # Format commits for AI
            summary_parts = ["## Recent Git Commits\n"]
            for commit in commits:
                summary_parts.append(f"### {commit.hash}: {commit.message}")
                summary_parts.append(f"*Author: {commit.author} | Date: {commit.date.strftime('%Y-%m-%d %H:%M')}*")
                if commit.files_changed:
                    summary_parts.append(f"**Files:** {', '.join(commit.files_changed)}")
                if commit.diff:
                    summary_parts.append(f"**Changes:**\n```\n{commit.diff[:500]}...\n```")
                summary_parts.append("")

            return "\n".join(summary_parts), len(commits), branch_info

        except Exception as e:
            return f"Error collecting git context: {e}", 0, {}

    def _collect_obsidian_context(self, days: int) -> tuple[str, int]:
        """Collect Obsidian context."""
        if not self.obsidian:
            return "Obsidian not configured.", 0

        try:
            notes = self.obsidian.get_recent_notes(days)
            summary = self.obsidian.summarize_notes(notes)
            return summary, len(notes)

        except Exception as e:
            return f"Error collecting Obsidian context: {e}", 0

    def _collect_ticktick_context(self) -> tuple[str, int]:
        """Collect TickTick context."""
        if not self.ticktick:
            return "TickTick not configured.", 0

        try:
            tasks = self.ticktick.get_active_tasks(limit=20)
            summary = self.ticktick.summarize_tasks(tasks)
            return summary, len(tasks)

        except Exception as e:
            return f"Error collecting TickTick context: {e}", 0

    def run(
        self,
        commit_count: int = 3,
        note_days: int = 1,
        show_welcome: bool = True
    ):
        """
        Run the context recovery agent and print results.

        Args:
            commit_count: Number of commits to analyze
            note_days: Days of notes to include
            show_welcome: Whether to show welcome header
        """
        try:
            # Show welcome
            if show_welcome:
                self.formatter.print_welcome()

            # Collect initial counts for progress display
            git_count = len(self.git.get_recent_commits(commit_count)) if self.git else 0
            notes_count = len(self.obsidian.get_recent_notes(note_days)) if self.obsidian else 0
            tasks_count = len(self.ticktick.get_active_tasks()) if self.ticktick else 0

            # Show progress
            self.formatter.print_analysis_progress(git_count, notes_count, tasks_count)

            # Recover context
            context = self.recover_context(commit_count, note_days)

            # Display results
            if context:
                self.formatter.print_context(context)
            else:
                self.formatter.print_no_context()

        except Exception as e:
            self.formatter.print_error(str(e))
            raise
