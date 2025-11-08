#!/usr/bin/env python3
"""
Agent 3: Git Commit Message Generator
======================================

Learning Objectives:
- Integrate LLMs with external tools (Git)
- Use LangChain framework basics
- Process structured data (git diffs)
- Generate conventional commit messages

Complexity: ⭐⭐ Intermediate
Framework: langchain-ollama + gitpython
"""

import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

try:
    from git import Repo, InvalidGitRepositoryError
except ImportError:
    print("Error: gitpython not installed. Run: pip install gitpython")
    sys.exit(1)

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


@dataclass
class GitChange:
    """Represents a file change in git."""
    file_path: str
    change_type: str  # added, modified, deleted
    diff: str
    additions: int
    deletions: int


class CommitMessageGenerator:
    """
    Generate semantic commit messages from git changes.

    This agent demonstrates:
    1. Tool integration (Git)
    2. Structured data processing
    3. LangChain basics
    4. Conventional commit formats
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://localhost:11434",
        repo_path: str = "."
    ):
        """Initialize the commit message generator."""
        self.model = model
        self.llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=0.3  # Lower for more consistent commit messages
        )

        # Initialize git repo
        try:
            self.repo = Repo(repo_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise ValueError(f"Not a git repository: {repo_path}")

    def get_staged_changes(self) -> List[GitChange]:
        """Get all staged changes."""
        changes = []

        # Get staged diff
        diff_index = self.repo.index.diff("HEAD", create_patch=True)

        for diff_item in diff_index:
            change = GitChange(
                file_path=diff_item.a_path or diff_item.b_path,
                change_type=self._get_change_type(diff_item),
                diff=diff_item.diff.decode('utf-8', errors='ignore') if diff_item.diff else "",
                additions=diff_item.diff.count(b'\n+') if diff_item.diff else 0,
                deletions=diff_item.diff.count(b'\n-') if diff_item.diff else 0
            )
            changes.append(change)

        return changes

    def _get_change_type(self, diff_item) -> str:
        """Determine the type of change."""
        if diff_item.new_file:
            return "added"
        elif diff_item.deleted_file:
            return "deleted"
        elif diff_item.renamed:
            return "renamed"
        else:
            return "modified"

    def generate_commit_message(
        self,
        changes: Optional[List[GitChange]] = None,
        conventional: bool = True,
        commit_type: Optional[str] = None
    ) -> str:
        """
        Generate a commit message from changes.

        Args:
            changes: List of changes (if None, uses staged changes)
            conventional: Use conventional commits format
            commit_type: Force specific commit type (feat, fix, etc.)

        Returns:
            Generated commit message
        """
        if changes is None:
            changes = self.get_staged_changes()

        if not changes:
            return "No changes to commit"

        # Build context about changes
        context = self._build_change_context(changes)

        # Build prompt
        prompt = self._build_prompt(context, conventional, commit_type)

        # Generate message
        message = self.llm.invoke(prompt)

        return message.strip()

    def _build_change_context(self, changes: List[GitChange]) -> str:
        """Build a context string describing all changes."""
        context_parts = []

        context_parts.append(f"Total files changed: {len(changes)}")

        total_additions = sum(c.additions for c in changes)
        total_deletions = sum(c.deletions for c in changes)
        context_parts.append(f"Total additions: +{total_additions}")
        context_parts.append(f"Total deletions: -{total_deletions}")

        context_parts.append("\nFiles changed:")
        for change in changes:
            context_parts.append(f"  - {change.file_path} ({change.change_type})")

        # Include diffs (truncated if too long)
        context_parts.append("\nDetailed changes:")
        for change in changes:
            context_parts.append(f"\n### {change.file_path}")
            # Truncate long diffs
            diff = change.diff[:500] if len(change.diff) > 500 else change.diff
            context_parts.append(diff)
            if len(change.diff) > 500:
                context_parts.append("... (diff truncated)")

        return "\n".join(context_parts)

    def _build_prompt(
        self,
        context: str,
        conventional: bool,
        commit_type: Optional[str]
    ) -> str:
        """Build the prompt for commit message generation."""

        if conventional:
            format_instructions = """Use conventional commits format:
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Keep description under 72 characters.
Be specific and clear about what changed."""
        else:
            format_instructions = """Write a clear, concise commit message.
First line: Brief summary (under 72 characters)
Keep it specific and actionable."""

        type_hint = f"\nCommit type should be: {commit_type}" if commit_type else ""

        prompt = f"""You are a senior engineer writing a git commit message.

Given these code changes, generate an appropriate commit message.

Changes:
{context}

{format_instructions}{type_hint}

Generate ONLY the commit message (no explanations or extra text):"""

        return prompt


def display_changes(changes: List[GitChange]):
    """Display changes in a formatted way."""
    console.print("\n[bold cyan]📝 Staged Changes:[/bold cyan]\n")

    for change in changes:
        color = {
            "added": "green",
            "modified": "yellow",
            "deleted": "red",
            "renamed": "blue"
        }.get(change.change_type, "white")

        console.print(
            f"  [{color}]{change.change_type.upper()}[/{color}] {change.file_path} "
            f"([green]+{change.additions}[/green]/[red]-{change.deletions}[/red])"
        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Git Commit Message Generator - Learn tool integration"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to git repository"
    )
    parser.add_argument(
        "--type",
        choices=["feat", "fix", "docs", "style", "refactor", "test", "chore"],
        help="Force specific commit type"
    )
    parser.add_argument(
        "--no-conventional",
        action="store_true",
        help="Don't use conventional commits format"
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model to use"
    )

    args = parser.parse_args()

    try:
        # Create generator
        generator = CommitMessageGenerator(
            model=args.model,
            repo_path=args.repo
        )

        # Display header
        console.print(Panel.fit(
            "[bold cyan]Git Commit Message Generator[/bold cyan]\n\n"
            f"Repository: [yellow]{generator.repo.working_dir}[/yellow]\n"
            f"Model: [yellow]{args.model}[/yellow]",
            border_style="cyan"
        ))

        # Get staged changes
        changes = generator.get_staged_changes()

        if not changes:
            console.print("\n[yellow]No staged changes found.[/yellow]")
            console.print("[dim]Stage changes with: git add <files>[/dim]")
            sys.exit(0)

        # Display changes
        display_changes(changes)

        # Generate commit message
        console.print("\n[dim]Generating commit message...[/dim]\n")

        message = generator.generate_commit_message(
            changes=changes,
            conventional=not args.no_conventional,
            commit_type=args.type
        )

        # Display result
        console.print(Panel(
            message,
            title="[bold green]Generated Commit Message[/bold green]",
            border_style="green"
        ))

        # Ask if user wants to commit
        console.print("\n[dim]To use this message:[/dim]")
        console.print(f'[cyan]git commit -m "{message}"[/cyan]')

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
