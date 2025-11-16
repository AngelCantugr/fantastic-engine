"""GitHub API client wrapper."""

from typing import List, Dict
from github import Github, PullRequest


class GitHubClient:
    """Wrapper for GitHub API operations."""

    def __init__(self, token: str, repo: str):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token
            repo: Repository in format "owner/repo"
        """
        self.client = Github(token)
        self.repo = self.client.get_repo(repo)

    def get_pr(self, pr_number: int) -> PullRequest:
        """Get pull request by number.

        Args:
            pr_number: PR number

        Returns:
            PullRequest object
        """
        # TODO: Implement
        raise NotImplementedError()

    def get_pr_diff(self, pr_number: int) -> str:
        """Get PR diff.

        Args:
            pr_number: PR number

        Returns:
            Diff string
        """
        # TODO: Fetch diff from GitHub
        raise NotImplementedError()

    def get_pr_files(self, pr_number: int) -> List[Dict]:
        """Get list of changed files in PR.

        Args:
            pr_number: PR number

        Returns:
            List of file metadata dicts
        """
        # TODO: Get changed files
        raise NotImplementedError()

    def post_review_comment(
        self,
        pr_number: int,
        file_path: str,
        line: int,
        body: str
    ):
        """Post inline review comment.

        Args:
            pr_number: PR number
            file_path: Path to file
            line: Line number
            body: Comment body (markdown)
        """
        # TODO: Post inline comment
        raise NotImplementedError()

    def post_pr_comment(self, pr_number: int, body: str):
        """Post general PR comment.

        Args:
            pr_number: PR number
            body: Comment body (markdown)
        """
        # TODO: Post PR comment
        raise NotImplementedError()
