"""
Automation suggestion module.
Maps toil patterns to specific automation strategies.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AutomationStrategy:
    """Represents an automation strategy for a toil pattern."""

    pattern_name: str
    tools: List[str]
    approach: str
    setup_steps: List[str]
    estimated_time_saved: str
    difficulty: str  # 'easy', 'medium', 'hard'
    resources: List[str]


class AutomationSuggester:
    """Suggests automation strategies for identified toil patterns."""

    def __init__(self):
        """Initialize the automation suggester with strategies."""
        self.strategies = self._build_strategies()

    def _build_strategies(self) -> Dict[str, AutomationStrategy]:
        """Build the database of automation strategies."""
        return {
            "Fix linting/formatting": AutomationStrategy(
                pattern_name="Fix linting/formatting",
                tools=["pre-commit", "black", "prettier", "eslint", "ruff"],
                approach="Pre-commit hooks",
                setup_steps=[
                    "Install pre-commit: pip install pre-commit",
                    "Create .pre-commit-config.yaml",
                    "Add formatters/linters to config",
                    "Run: pre-commit install",
                    "Test: pre-commit run --all-files",
                ],
                estimated_time_saved="5-10 hours/month",
                difficulty="easy",
                resources=[
                    "https://pre-commit.com/",
                    "https://black.readthedocs.io/",
                    "https://prettier.io/",
                ],
            ),
            "Update dependencies": AutomationStrategy(
                pattern_name="Update dependencies",
                tools=["Dependabot", "Renovate", "GitHub Actions"],
                approach="Automated dependency updates",
                setup_steps=[
                    "Enable Dependabot in GitHub repo settings",
                    "Or: Add .github/dependabot.yml config",
                    "Configure update frequency and package ecosystems",
                    "Set up auto-merge for minor/patch updates",
                    "Review and approve major updates",
                ],
                estimated_time_saved="3-5 hours/month",
                difficulty="easy",
                resources=[
                    "https://docs.github.com/en/code-security/dependabot",
                    "https://www.mend.io/renovate/",
                ],
            ),
            "Fix typos": AutomationStrategy(
                pattern_name="Fix typos",
                tools=["codespell", "typos", "cspell", "GitHub Actions"],
                approach="Spell checker in CI",
                setup_steps=[
                    "Add spell checker to CI pipeline",
                    "Install: pip install codespell or cargo install typos-cli",
                    "Create .codespellrc or .typos.toml config",
                    "Add to GitHub Actions workflow",
                    "Configure ignore list for technical terms",
                ],
                estimated_time_saved="2-3 hours/month",
                difficulty="easy",
                resources=[
                    "https://github.com/codespell-project/codespell",
                    "https://github.com/crate-ci/typos",
                ],
            ),
            "Regenerate files": AutomationStrategy(
                pattern_name="Regenerate files",
                tools=["GitHub Actions", "Make", "just", "pre-commit"],
                approach="Automated code generation",
                setup_steps=[
                    "Identify generation commands (e.g., protoc, openapi-generator)",
                    "Create script to run generation",
                    "Add to pre-commit hooks or CI",
                    "Verify generated files in CI",
                    "Fail build if files are out of sync",
                ],
                estimated_time_saved="2-4 hours/month",
                difficulty="medium",
                resources=[
                    "https://docs.github.com/en/actions",
                    "https://pre-commit.com/",
                ],
            ),
            "Update copyright/year": AutomationStrategy(
                pattern_name="Update copyright/year",
                tools=["GitHub Actions", "cron job", "script"],
                approach="Automated copyright updates",
                setup_steps=[
                    "Create script to update copyright year",
                    "Use sed/awk or dedicated tool",
                    "Run annually via GitHub Actions (scheduled)",
                    "Or: Use dynamic copyright in code",
                    "Create PR automatically with updates",
                ],
                estimated_time_saved="1 hour/year",
                difficulty="easy",
                resources=[
                    "https://github.com/marketplace/actions/update-copyright",
                ],
            ),
            "Merge conflicts": AutomationStrategy(
                pattern_name="Merge conflicts",
                tools=["Rebase workflow", "GitHub merge queue", "Bors"],
                approach="Better merge strategy",
                setup_steps=[
                    "Switch to rebase workflow instead of merge",
                    "Use 'git pull --rebase' by default",
                    "Configure: git config pull.rebase true",
                    "Enable GitHub merge queue for sequential merges",
                    "Keep branches short-lived and up to date",
                ],
                estimated_time_saved="3-5 hours/month",
                difficulty="medium",
                resources=[
                    "https://git-scm.com/book/en/v2/Git-Branching-Rebasing",
                    "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue",
                ],
            ),
            "Fix tests": AutomationStrategy(
                pattern_name="Fix tests",
                tools=["pytest-xdist", "test retry", "better isolation"],
                approach="Improve test reliability",
                setup_steps=[
                    "Identify flaky tests",
                    "Add test isolation (fixtures, cleanup)",
                    "Use test retry for network-dependent tests",
                    "Run tests in parallel with pytest-xdist",
                    "Add CI job to detect flaky tests",
                ],
                estimated_time_saved="5-8 hours/month",
                difficulty="hard",
                resources=[
                    "https://docs.pytest.org/en/stable/how-to/flaky.html",
                    "https://github.com/pytest-dev/pytest-xdist",
                ],
            ),
            "Update documentation": AutomationStrategy(
                pattern_name="Update documentation",
                tools=["docgen", "sphinx", "typedoc", "CI checks"],
                approach="Auto-generated docs",
                setup_steps=[
                    "Use doc generation tools (sphinx, typedoc, etc.)",
                    "Generate docs from code comments/docstrings",
                    "Add CI check to verify docs are up to date",
                    "Auto-deploy docs on merge to main",
                    "Use GitHub Pages or similar",
                ],
                estimated_time_saved="3-5 hours/month",
                difficulty="medium",
                resources=[
                    "https://www.sphinx-doc.org/",
                    "https://typedoc.org/",
                    "https://squidfunk.github.io/mkdocs-material/",
                ],
            ),
        }

    def get_suggestion(
        self, pattern_name: str
    ) -> Optional[AutomationStrategy]:
        """
        Get automation suggestion for a specific toil pattern.

        Args:
            pattern_name: Name of the toil pattern

        Returns:
            AutomationStrategy if found, None otherwise
        """
        return self.strategies.get(pattern_name)

    def get_all_suggestions(self) -> List[AutomationStrategy]:
        """Get all automation strategies."""
        return list(self.strategies.values())

    def rank_by_impact(
        self, pattern_frequency: List[tuple]
    ) -> List[tuple]:
        """
        Rank automation suggestions by impact (frequency + time saved).

        Args:
            pattern_frequency: List of (pattern_name, count, category)

        Returns:
            List of (pattern_name, count, strategy, impact_score)
        """
        ranked = []

        for pattern_name, count, category in pattern_frequency:
            strategy = self.get_suggestion(pattern_name)
            if strategy:
                # Calculate impact score (simple heuristic)
                difficulty_weight = {
                    "easy": 1.0,
                    "medium": 0.7,
                    "hard": 0.4,
                }
                impact_score = count * difficulty_weight.get(
                    strategy.difficulty, 0.5
                )
                ranked.append((pattern_name, count, strategy, impact_score))

        # Sort by impact score
        return sorted(ranked, key=lambda x: x[3], reverse=True)

    def generate_report(
        self, pattern_frequency: List[tuple]
    ) -> Dict[str, any]:
        """
        Generate a comprehensive automation report.

        Args:
            pattern_frequency: List of (pattern_name, count, category)

        Returns:
            Dictionary with report data
        """
        ranked = self.rank_by_impact(pattern_frequency)

        report = {
            "total_toil_commits": sum(
                count for _, count, _ in pattern_frequency
            ),
            "unique_patterns": len(pattern_frequency),
            "recommendations": [],
        }

        for pattern_name, count, strategy, impact_score in ranked:
            recommendation = {
                "pattern": pattern_name,
                "frequency": count,
                "impact_score": round(impact_score, 2),
                "tools": strategy.tools,
                "approach": strategy.approach,
                "setup_steps": strategy.setup_steps,
                "estimated_time_saved": strategy.estimated_time_saved,
                "difficulty": strategy.difficulty,
                "resources": strategy.resources,
            }
            report["recommendations"].append(recommendation)

        return report


def main():
    """Example usage of AutomationSuggester."""
    suggester = AutomationSuggester()

    # Sample pattern frequency data
    pattern_frequency = [
        ("Fix linting/formatting", 47, "code_quality"),
        ("Update dependencies", 32, "dependencies"),
        ("Fix typos", 28, "documentation"),
    ]

    print("Automation Suggestions:")
    ranked = suggester.rank_by_impact(pattern_frequency)

    for pattern_name, count, strategy, impact_score in ranked:
        print(f"\n{pattern_name} ({count} occurrences)")
        print(f"  Impact Score: {impact_score:.1f}")
        print(f"  Tools: {', '.join(strategy.tools)}")
        print(f"  Difficulty: {strategy.difficulty}")
        print(f"  Time Saved: {strategy.estimated_time_saved}")


if __name__ == "__main__":
    main()
