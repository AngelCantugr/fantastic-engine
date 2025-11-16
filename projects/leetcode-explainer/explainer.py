#!/usr/bin/env python3
"""
LeetCode Solution Explainer Agent

Provides multi-level, ADHD-friendly explanations of LeetCode solutions
using GPT-4 and rich terminal formatting.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

import click
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import requests
from diskcache import Cache

# Load environment variables
load_dotenv()

# Initialize
console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
cache = Cache(os.getenv("CACHE_DIR", ".cache/explanations"))


class ExplanationLevel(Enum):
    """Explanation depth levels"""
    ELI5 = 1  # Explain Like I'm 5
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class Difficulty(Enum):
    """Problem difficulty"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass
class Pattern:
    """Algorithmic pattern information"""
    name: str
    description: str
    when_to_use: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)


@dataclass
class TraceStep:
    """Single step in code execution trace"""
    step_number: int
    code_line: str
    state: Dict[str, Any]
    explanation: str


@dataclass
class ComplexityAnalysis:
    """Time and space complexity analysis"""
    time_complexity: str
    time_explanation: str
    space_complexity: str
    space_explanation: str
    best_case: Optional[str] = None
    worst_case: Optional[str] = None


@dataclass
class Alternative:
    """Alternative solution approach"""
    name: str
    time_complexity: str
    space_complexity: str
    description: str
    when_to_use: str
    code_snippet: Optional[str] = None


@dataclass
class Explanation:
    """Complete problem explanation"""
    problem_id: int
    problem_title: str
    difficulty: Difficulty
    quick_summary: str
    pattern: Pattern
    explanation_levels: Dict[int, str]
    step_by_step: List[TraceStep]
    complexity: ComplexityAnalysis
    alternatives: List[Alternative]
    common_mistakes: List[str]
    similar_problems: List[int]
    learning_tips: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class LeetCodeExplainer:
    """Main explainer class"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.client = OpenAI(api_key=self.api_key)
        self.cache_enabled = os.getenv("ENABLE_CACHING", "true").lower() == "true"

    def fetch_problem(self, problem_id: int) -> Dict[str, Any]:
        """Fetch problem details from LeetCode"""
        # TODO: Implement LeetCode API/scraping
        # For now, return mock data
        console.print(f"[yellow]⚠️  Fetching problem {problem_id} (mock data)[/yellow]")
        return {
            "id": problem_id,
            "title": "Two Sum",
            "difficulty": "Easy",
            "description": "Given an array of integers nums and an integer target...",
            "example_code": """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""".strip()
        }

    def generate_explanation_prompt(
        self,
        problem: Dict[str, Any],
        code: str,
        level: ExplanationLevel
    ) -> str:
        """Generate prompt for GPT-4"""
        level_descriptions = {
            ExplanationLevel.ELI5: "using simple analogies a 5-year-old could understand",
            ExplanationLevel.BEGINNER: "for someone new to programming",
            ExplanationLevel.INTERMEDIATE: "for someone with basic algorithms knowledge",
            ExplanationLevel.ADVANCED: "with edge cases and optimizations",
            ExplanationLevel.EXPERT: "with mathematical proofs and complexity analysis"
        }

        return f"""
You are an expert programming tutor specializing in LeetCode problem explanations.
Your explanations are ADHD-friendly: concise, visual, and well-structured.

Problem: {problem['title']} (#{problem['id']})
Difficulty: {problem['difficulty']}

Code to explain:
```python
{code}
```

Provide a comprehensive explanation at {level_descriptions[level]} level.

Include:
1. Quick Summary (2-3 sentences)
2. Algorithmic Pattern (name and when to use it)
3. Detailed Explanation
4. Step-by-step code trace with example input
5. Time and space complexity analysis
6. Alternative approaches with trade-offs
7. Common mistakes to avoid
8. 3-5 similar problems to practice
9. Learning tips for mastering this pattern

Format your response as JSON with these keys:
{{
    "quick_summary": "...",
    "pattern_name": "...",
    "pattern_description": "...",
    "when_to_use_pattern": ["...", "..."],
    "explanation": "...",
    "trace_steps": [
        {{"step": 1, "code": "...", "state": {{}}, "explanation": "..."}},
        ...
    ],
    "time_complexity": "O(...)",
    "time_explanation": "...",
    "space_complexity": "O(...)",
    "space_explanation": "...",
    "alternatives": [
        {{"name": "...", "time": "...", "space": "...", "description": "...", "when_to_use": "..."}}
    ],
    "common_mistakes": ["...", "..."],
    "similar_problems": [1, 2, 3],
    "learning_tips": ["...", "..."]
}}
"""

    def explain(
        self,
        problem_id: Optional[int] = None,
        code: Optional[str] = None,
        level: int = 3,
        focus: Optional[str] = None
    ) -> Explanation:
        """Generate explanation for a solution"""

        # Check cache
        cache_key = f"{problem_id}_{level}_{focus}"
        if self.cache_enabled and cache_key in cache:
            console.print("[green]✓ Loading from cache[/green]")
            return cache[cache_key]

        # Fetch problem
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching problem...", total=None)
            problem = self.fetch_problem(problem_id)

            # Use provided code or fetch solution
            if not code:
                code = problem.get("example_code", "")

            progress.update(task, description="Generating explanation...")

            # Generate explanation with GPT-4
            explanation_level = ExplanationLevel(level)
            prompt = self.generate_explanation_prompt(problem, code, explanation_level)

            # TODO: Actually call OpenAI API
            # response = self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[{"role": "user", "content": prompt}],
            #     response_format={"type": "json_object"}
            # )

            # Mock explanation for now
            explanation = self._create_mock_explanation(problem, level)

            progress.update(task, description="✓ Done!", completed=True)

        # Cache result
        if self.cache_enabled:
            cache[cache_key] = explanation

        return explanation

    def _create_mock_explanation(self, problem: Dict, level: int) -> Explanation:
        """Create mock explanation (temporary)"""
        return Explanation(
            problem_id=problem["id"],
            problem_title=problem["title"],
            difficulty=Difficulty.EASY,
            quick_summary="Use a hash table to store complements for O(n) lookup time.",
            pattern=Pattern(
                name="Hash Table Lookup",
                description="Store data for O(1) access to find complements/pairs",
                when_to_use=["Finding pairs", "O(1) lookup needed", "Can trade space for time"],
                related_patterns=["Two Pointers", "Sliding Window"]
            ),
            explanation_levels={
                level: "The problem asks us to find two numbers that add up to a target..."
            },
            step_by_step=[
                TraceStep(
                    step_number=1,
                    code_line="seen = {}",
                    state={"seen": {}, "i": None, "num": None},
                    explanation="Initialize empty hash table"
                ),
                TraceStep(
                    step_number=2,
                    code_line="for i, num in enumerate(nums):",
                    state={"seen": {}, "i": 0, "num": 2, "nums": [2, 7, 11, 15]},
                    explanation="Start iterating, i=0, num=2"
                ),
            ],
            complexity=ComplexityAnalysis(
                time_complexity="O(n)",
                time_explanation="Single pass through array with O(1) hash lookups",
                space_complexity="O(n)",
                space_explanation="Hash table stores up to n elements"
            ),
            alternatives=[
                Alternative(
                    name="Brute Force",
                    time_complexity="O(n²)",
                    space_complexity="O(1)",
                    description="Check every pair with nested loops",
                    when_to_use="Array is very small (n < 10)"
                )
            ],
            common_mistakes=[
                "Using the same element twice",
                "Not handling duplicates correctly",
                "Assuming array is sorted"
            ],
            similar_problems=[167, 170, 653],
            learning_tips=[
                "Practice the 'complement' thinking pattern",
                "Remember: Hash tables trade space for time",
                "Always check for edge cases"
            ]
        )

    def display(self, explanation: Explanation):
        """Display explanation with rich formatting"""

        # Header
        console.print()
        console.print(Panel.fit(
            f"🧠 [bold cyan]LeetCode Solution Explainer[/bold cyan]\n"
            f"Problem #{explanation.problem_id}: {explanation.problem_title}",
            border_style="cyan"
        ))

        # Quick Summary
        console.print("\n📊 [bold]QUICK SUMMARY[/bold]")
        console.rule(style="dim")
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        table.add_row("Pattern:", explanation.pattern.name)
        table.add_row("Difficulty:", explanation.difficulty.value)
        table.add_row("Time:", explanation.complexity.time_complexity)
        table.add_row("Space:", explanation.complexity.space_complexity)
        table.add_row("Key Insight:", explanation.quick_summary)
        console.print(table)

        # Main Explanation
        console.print("\n🎯 [bold]EXPLANATION[/bold]")
        console.rule(style="dim")
        level = list(explanation.explanation_levels.keys())[0]
        console.print(explanation.explanation_levels[level])

        # Step-by-step Trace
        console.print("\n🔍 [bold]STEP-BY-STEP TRACE[/bold]")
        console.rule(style="dim")
        for step in explanation.step_by_step:
            console.print(f"[cyan]Step {step.step_number}:[/cyan] {step.explanation}")
            console.print(f"  [dim]{step.code_line}[/dim]")
            console.print(f"  State: {step.state}")

        # Complexity
        console.print("\n⏱️  [bold]COMPLEXITY ANALYSIS[/bold]")
        console.rule(style="dim")
        console.print(f"[green]Time:[/green] {explanation.complexity.time_complexity}")
        console.print(f"  {explanation.complexity.time_explanation}")
        console.print(f"[green]Space:[/green] {explanation.complexity.space_complexity}")
        console.print(f"  {explanation.complexity.space_explanation}")

        # Pattern
        console.print(f"\n🎨 [bold]PATTERN: {explanation.pattern.name}[/bold]")
        console.rule(style="dim")
        console.print(explanation.pattern.description)
        console.print("\nWhen to use:")
        for use_case in explanation.pattern.when_to_use:
            console.print(f"  ✓ {use_case}")

        # Alternatives
        console.print("\n🔄 [bold]ALTERNATIVE APPROACHES[/bold]")
        console.rule(style="dim")
        for i, alt in enumerate(explanation.alternatives, 1):
            console.print(f"{i}. [cyan]{alt.name}[/cyan] ({alt.time_complexity} time, {alt.space_complexity} space)")
            console.print(f"   {alt.description}")
            console.print(f"   [dim]Use when: {alt.when_to_use}[/dim]")

        # Common Mistakes
        console.print("\n⚠️  [bold]COMMON MISTAKES[/bold]")
        console.rule(style="dim")
        for mistake in explanation.common_mistakes:
            console.print(f"  ❌ {mistake}")

        # Learning Tips
        console.print("\n💡 [bold]LEARNING TIPS[/bold]")
        console.rule(style="dim")
        for tip in explanation.learning_tips:
            console.print(f"  ✓ {tip}")

        console.print()


@click.command()
@click.option("--id", "problem_id", type=int, help="LeetCode problem ID")
@click.option("--url", help="LeetCode problem URL")
@click.option("--code", type=click.Path(exists=True), help="Path to code file")
@click.option("--level", type=click.IntRange(1, 5), default=3, help="Explanation level (1-5)")
@click.option("--focus", type=click.Choice(["complexity", "patterns", "alternatives"]), help="Focus area")
@click.option("--interactive", is_flag=True, help="Interactive mode")
@click.option("--export", type=click.Path(), help="Export to file")
def main(problem_id, url, code, level, focus, interactive, export):
    """LeetCode Solution Explainer - ADHD-friendly solution breakdowns"""

    console.print("[bold magenta]🧠 LeetCode Solution Explainer[/bold magenta]\n")

    # Extract problem ID from URL if provided
    if url and not problem_id:
        # TODO: Parse problem ID from URL
        problem_id = 1

    if not problem_id:
        console.print("[red]Error: Provide --id or --url[/red]")
        return

    # Load code from file if provided
    code_content = None
    if code:
        with open(code, "r") as f:
            code_content = f.read()

    # Create explainer and generate explanation
    explainer = LeetCodeExplainer()
    explanation = explainer.explain(
        problem_id=problem_id,
        code=code_content,
        level=level,
        focus=focus
    )

    # Display
    explainer.display(explanation)

    # Export if requested
    if export:
        # TODO: Implement export functionality
        console.print(f"\n[green]✓ Exported to {export}[/green]")


if __name__ == "__main__":
    main()
