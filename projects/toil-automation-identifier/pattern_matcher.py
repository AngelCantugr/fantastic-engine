"""
Pattern matching module for identifying toil in commit messages.
Uses regex patterns and optional AI analysis.
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import os


class ToilPattern:
    """Represents a toil pattern with its detection rule."""

    def __init__(
        self,
        name: str,
        patterns: List[str],
        category: str,
        description: str = "",
    ):
        """
        Initialize a toil pattern.

        Args:
            name: Human-readable name of the pattern
            patterns: List of regex patterns to match
            category: Category of toil (linting, deps, docs, etc.)
            description: Optional description
        """
        self.name = name
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.category = category
        self.description = description

    def matches(self, message: str) -> bool:
        """Check if a commit message matches this pattern."""
        return any(pattern.search(message) for pattern in self.patterns)


# Define common toil patterns
TOIL_PATTERNS = [
    ToilPattern(
        name="Fix linting/formatting",
        patterns=[
            r"\bfix.*lint",
            r"\brun.*lint",
            r"\bformat.*code",
            r"\brun.*prettier",
            r"\brun.*black",
            r"\bfix.*formatting",
            r"\beslint.*fix",
            r"\bprettier\b",
        ],
        category="code_quality",
        description="Manual linting and formatting fixes",
    ),
    ToilPattern(
        name="Update dependencies",
        patterns=[
            r"\bupdate.*dep",
            r"\bbump.*version",
            r"\bupgrade.*package",
            r"\bnpm.*update",
            r"\bpip.*upgrade",
            r"\bcargo.*update",
            r"\bgo.*mod.*tidy",
            r"\bpackage.*update",
        ],
        category="dependencies",
        description="Manual dependency updates",
    ),
    ToilPattern(
        name="Fix typos",
        patterns=[
            r"\bfix.*typo",
            r"\btypo\b",
            r"\bspelling",
            r"\bfix.*spelling",
            r"\bwording",
        ],
        category="documentation",
        description="Typo and spelling corrections",
    ),
    ToilPattern(
        name="Regenerate files",
        patterns=[
            r"\bregenerate",
            r"\brebuild",
            r"\bupdate.*generated",
            r"\bcodegen",
            r"\bgenerate.*types",
            r"\bupdate.*lockfile",
        ],
        category="codegen",
        description="Regenerating auto-generated files",
    ),
    ToilPattern(
        name="Update copyright/year",
        patterns=[
            r"\bupdate.*copyright",
            r"\bupdate.*year",
            r"\bcopyright.*\d{4}",
        ],
        category="maintenance",
        description="Updating copyright notices",
    ),
    ToilPattern(
        name="Merge conflicts",
        patterns=[
            r"\bresolve.*conflict",
            r"\bmerge.*conflict",
            r"\bfix.*conflict",
            r"\bconflict.*resolution",
        ],
        category="git",
        description="Resolving merge conflicts",
    ),
    ToilPattern(
        name="Fix tests",
        patterns=[
            r"\bfix.*test",
            r"\bfix.*failing.*test",
            r"\bupdate.*snapshot",
            r"\bfix.*flaky",
        ],
        category="testing",
        description="Fixing broken or flaky tests",
    ),
    ToilPattern(
        name="Update documentation",
        patterns=[
            r"\bupdate.*docs",
            r"\bupdate.*readme",
            r"\bfix.*docs",
            r"\bdocumentation.*update",
        ],
        category="documentation",
        description="Manual documentation updates",
    ),
]


class PatternMatcher:
    """Matches commit messages against toil patterns."""

    def __init__(
        self,
        patterns: Optional[List[ToilPattern]] = None,
        use_ai: bool = False,
        ai_provider: str = "none",
    ):
        """
        Initialize the pattern matcher.

        Args:
            patterns: Custom patterns (default: use built-in TOIL_PATTERNS)
            use_ai: Whether to use AI for pattern detection
            ai_provider: AI provider to use ('openai', 'ollama', 'none')
        """
        self.patterns = patterns or TOIL_PATTERNS
        self.use_ai = use_ai
        self.ai_provider = ai_provider

    def analyze_commits(
        self, commit_messages: List[str]
    ) -> Dict[str, List[str]]:
        """
        Analyze commit messages and categorize by toil pattern.

        Args:
            commit_messages: List of commit message strings

        Returns:
            Dictionary mapping pattern names to matching commit messages
        """
        matches = {pattern.name: [] for pattern in self.patterns}

        for message in commit_messages:
            for pattern in self.patterns:
                if pattern.matches(message):
                    matches[pattern.name].append(message)

        # Filter out patterns with no matches
        return {k: v for k, v in matches.items() if v}

    def get_pattern_frequency(
        self, commit_messages: List[str]
    ) -> List[Tuple[str, int, str]]:
        """
        Get toil patterns ranked by frequency.

        Args:
            commit_messages: List of commit messages

        Returns:
            List of tuples: (pattern_name, count, category)
        """
        matches = self.analyze_commits(commit_messages)
        frequency = []

        for pattern in self.patterns:
            count = len(matches.get(pattern.name, []))
            if count > 0:
                frequency.append((pattern.name, count, pattern.category))

        # Sort by frequency (descending)
        return sorted(frequency, key=lambda x: x[1], reverse=True)

    def get_category_summary(
        self, commit_messages: List[str]
    ) -> Dict[str, int]:
        """
        Get summary of toil by category.

        Args:
            commit_messages: List of commit messages

        Returns:
            Dictionary mapping categories to total counts
        """
        category_counts = Counter()

        for message in commit_messages:
            for pattern in self.patterns:
                if pattern.matches(message):
                    category_counts[pattern.category] += 1

        return dict(category_counts)


def main():
    """Example usage of PatternMatcher."""
    # Sample commit messages
    sample_commits = [
        "fix: run prettier on all files",
        "chore: update dependencies",
        "fix: typo in README",
        "fix: resolve merge conflict",
        "chore: run black formatter",
        "fix: update dependency versions",
        "docs: fix spelling errors",
        "fix: regenerate lockfile",
    ]

    matcher = PatternMatcher()

    print("Pattern Analysis:")
    frequency = matcher.get_pattern_frequency(sample_commits)
    for pattern_name, count, category in frequency:
        print(f"  {pattern_name}: {count} ({category})")

    print("\nCategory Summary:")
    summary = matcher.get_category_summary(sample_commits)
    for category, count in summary.items():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
