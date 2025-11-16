"""
Git repository analysis module.
Extracts commit messages and metadata from git repositories.
"""

import git
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class GitAnalyzer:
    """Analyzes git repositories to extract commit information."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize the GitAnalyzer.

        Args:
            repo_path: Path to the git repository (default: current directory)
        """
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid git repository: {repo_path}")

    def get_commits(
        self,
        max_count: int = 200,
        branch: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, any]]:
        """
        Extract commit messages from the repository.

        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch name to analyze (default: current branch)
            since: Only commits after this date

        Returns:
            List of commit dictionaries with message, author, date, and hash
        """
        commits = []

        # Determine which branch to analyze
        if branch:
            try:
                commit_iter = self.repo.iter_commits(branch, max_count=max_count)
            except git.GitCommandError:
                raise ValueError(f"Branch '{branch}' not found")
        else:
            commit_iter = self.repo.iter_commits(max_count=max_count)

        for commit in commit_iter:
            # Skip if commit is older than 'since' date
            if since and commit.committed_datetime < since:
                continue

            commit_data = {
                "hash": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": commit.committed_datetime,
                "files_changed": len(commit.stats.files),
            }
            commits.append(commit_data)

        return commits

    def get_commit_messages(self, max_count: int = 200) -> List[str]:
        """
        Get just the commit messages (simplified version).

        Args:
            max_count: Maximum number of commits

        Returns:
            List of commit message strings
        """
        commits = self.get_commits(max_count=max_count)
        return [commit["message"] for commit in commits]

    def get_repository_info(self) -> Dict[str, any]:
        """
        Get basic repository information.

        Returns:
            Dictionary with repo metadata
        """
        try:
            active_branch = self.repo.active_branch.name
        except TypeError:
            active_branch = "detached HEAD"

        return {
            "path": self.repo.working_dir,
            "active_branch": active_branch,
            "total_commits": sum(1 for _ in self.repo.iter_commits()),
            "remotes": [remote.name for remote in self.repo.remotes],
            "is_dirty": self.repo.is_dirty(),
        }

    def analyze_commit_frequency(
        self, commits: List[Dict[str, any]]
    ) -> Dict[str, int]:
        """
        Analyze commit frequency by author.

        Args:
            commits: List of commit dictionaries

        Returns:
            Dictionary mapping author names to commit counts
        """
        frequency = {}
        for commit in commits:
            author = commit["author"]
            frequency[author] = frequency.get(author, 0) + 1
        return frequency


def main():
    """Example usage of GitAnalyzer."""
    analyzer = GitAnalyzer()

    print("Repository Info:")
    info = analyzer.get_repository_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\nLast 10 commits:")
    commits = analyzer.get_commits(max_count=10)
    for commit in commits:
        print(f"  [{commit['hash']}] {commit['message'][:60]}")


if __name__ == "__main__":
    main()
