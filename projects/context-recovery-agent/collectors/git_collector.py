"""Git commit collector."""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    diff: str


class GitCollector:
    """Collects context from git commits."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"{repo_path} is not a git repository")

    def get_recent_commits(self, count: int = 3) -> List[GitCommit]:
        """Get the most recent commits."""
        commits = []

        # Get commit hashes
        result = subprocess.run(
            ["git", "log", f"-{count}", "--format=%H"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        hashes = result.stdout.strip().split('\n')

        for commit_hash in hashes:
            if commit_hash:
                commits.append(self._get_commit_details(commit_hash))

        return commits

    def _get_commit_details(self, commit_hash: str) -> GitCommit:
        """Get detailed information about a commit."""
        # Get commit info
        result = subprocess.run(
            ["git", "show", "--format=%an%n%at%n%s%n%b", "--name-only", commit_hash],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.split('\n')

        # Parse output
        author = lines[0]
        timestamp = int(lines[1])
        message = lines[2]
        if len(lines) > 3 and lines[3] and not lines[3].startswith('diff'):
            message += '\n' + lines[3]

        # Find where file list starts (after empty line)
        file_start = 4
        for i in range(4, len(lines)):
            if lines[i] == '':
                file_start = i + 1
                break

        # Get changed files
        files_changed = [f for f in lines[file_start:] if f and not f.startswith('diff')]

        # Get diff
        diff_result = subprocess.run(
            ["git", "show", "--format=", commit_hash],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        return GitCommit(
            hash=commit_hash[:7],
            author=author,
            date=datetime.fromtimestamp(timestamp),
            message=message.strip(),
            files_changed=files_changed[:10],  # Limit to 10 files
            diff=self._summarize_diff(diff_result.stdout)
        )

    def _summarize_diff(self, diff: str) -> str:
        """Summarize diff to key changes."""
        lines = diff.split('\n')

        # Count additions and deletions
        additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))

        # Extract meaningful changes (skip binary files, large chunks)
        meaningful_lines = []
        for line in lines[:100]:  # Limit to first 100 lines
            if line.startswith('@@'):
                meaningful_lines.append(line)
            elif line.startswith('+') and not line.startswith('+++'):
                meaningful_lines.append(line)
            elif line.startswith('-') and not line.startswith('---'):
                meaningful_lines.append(line)

        summary = f"+{additions} -{deletions} lines\n"
        if meaningful_lines:
            summary += '\n'.join(meaningful_lines[:20])  # First 20 meaningful lines

        return summary

    def get_current_branch(self) -> str:
        """Get current git branch."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def get_branch_info(self) -> Dict[str, any]:
        """Get current branch information."""
        branch = self.get_current_branch()

        # Get commits ahead/behind
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", f"origin/{branch}...{branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                behind, ahead = map(int, result.stdout.strip().split())
            else:
                behind, ahead = 0, 0
        except (ValueError, subprocess.SubprocessError):
            behind, ahead = 0, 0

        return {
            "branch": branch,
            "commits_ahead": ahead,
            "commits_behind": behind,
        }
