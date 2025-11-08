#!/usr/bin/env python3
"""
Agent 2: Code Review Assistant
===============================

Learning Objectives:
- Master structured prompt engineering
- Use few-shot learning effectively
- Create reusable prompt templates
- Parse and format structured outputs

Complexity: ⭐⭐ Beginner-Intermediate
Framework: ollama + prompt templates
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

console = Console()


@dataclass
class ReviewResult:
    """Structured code review result."""
    summary: str
    rating: str
    strengths: List[str]
    issues: List[str]
    suggestions: List[str]
    security_notes: Optional[str] = None
    performance_notes: Optional[str] = None


class PromptTemplate:
    """
    Manages prompt templates for different review types.

    This demonstrates how to create reusable, structured prompts
    with placeholders that can be filled in at runtime.
    """

    SYSTEM_MESSAGE = """You are a senior software engineer conducting a thorough code review.

You have 10+ years of experience and are known for:
- Catching subtle bugs and security issues
- Providing actionable, specific feedback
- Balancing criticism with positive reinforcement
- Teaching junior engineers through your reviews

Your reviews are:
- Constructive and helpful (not harsh)
- Specific with examples
- Focused on improvement
- Well-structured and easy to read"""

    GENERAL_REVIEW = """Review the following code comprehensively.

Analyze these aspects:
1. **Correctness**: Does it work as intended?
2. **Readability**: Is it easy to understand?
3. **Maintainability**: Is it easy to modify?
4. **Best Practices**: Does it follow conventions?
5. **Testing**: Is it testable?

{few_shot_examples}

Now review this code:

```{language}
{code}
```

Provide a structured review with:
- Summary: Brief overall assessment
- Rating: X/10 with justification
- Strengths: What's done well (list)
- Issues: Problems found (list with severity)
- Suggestions: Specific improvements (list)

Be specific and provide examples where helpful."""

    SECURITY_REVIEW = """Conduct a security-focused code review.

Check for common vulnerabilities:
- SQL Injection
- Cross-Site Scripting (XSS)
- Authentication/Authorization issues
- Input validation
- Sensitive data exposure
- Insecure dependencies

{few_shot_examples}

Code to review:

```{language}
{code}
```

Provide:
- Security Rating: X/10
- Vulnerabilities: List any security issues (with severity: Critical/High/Medium/Low)
- Recommendations: Specific fixes
- Good Practices: Security measures already in place"""

    PERFORMANCE_REVIEW = """Analyze this code for performance.

Consider:
- Time complexity (Big O notation)
- Space complexity
- Unnecessary operations
- Potential bottlenecks
- Scalability issues

{few_shot_examples}

Code to review:

```{language}
{code}
```

Provide:
- Performance Rating: X/10
- Complexity Analysis: Time and space complexity
- Issues: Performance problems found
- Optimizations: Specific suggestions with examples"""

    STYLE_REVIEW = """Review code style and conventions.

Check:
- Naming conventions
- Code formatting
- Documentation (docstrings/comments)
- PEP 8 compliance (if Python)
- Consistency

{few_shot_examples}

Code to review:

```{language}
{code}
```

Provide:
- Style Rating: X/10
- Issues: Style violations
- Suggestions: How to improve code style
- Good Practices: Well-styled elements"""

    FEW_SHOT_EXAMPLES = """
Example Review 1:

Code:
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total
```

Review:
- Rating: 6/10
- Strengths: Simple, clear logic
- Issues:
  1. No input validation
  2. Missing type hints
  3. No docstring
  4. Assumes 'price' key exists
- Suggestions:
  1. Add type hints: `def calculate_total(items: List[Dict[str, float]]) -> float:`
  2. Add docstring explaining purpose
  3. Validate items and handle missing 'price' gracefully

Example Review 2:

Code:
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

Review:
- Rating: 2/10
- Strengths: Concise
- Issues:
  1. **CRITICAL: SQL Injection vulnerability!**
  2. No input validation
  3. Returns raw query result
  4. Missing type hints and docstring
- Suggestions:
  1. Use parameterized queries: `"SELECT * FROM users WHERE id = ?"`, `(user_id,)`
  2. Validate user_id is an integer
  3. Return a typed User object
  4. Add proper error handling

---
"""


class CodeReviewAgent:
    """
    AI-powered code review assistant using structured prompts.

    This agent demonstrates:
    1. Template-based prompt engineering
    2. Few-shot learning with examples
    3. Structured output parsing
    4. Different review modes
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3  # Lower for more consistent reviews
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.client = httpx.Client(timeout=120.0)
        self.templates = PromptTemplate()

    def review_code(
        self,
        code: str,
        review_type: str = "general",
        language: str = "python",
        include_examples: bool = True
    ) -> str:
        """
        Review code using specified review type.

        Args:
            code: The code to review
            review_type: Type of review (general, security, performance, style)
            language: Programming language (for syntax highlighting)
            include_examples: Whether to include few-shot examples

        Returns:
            The review text
        """
        # Get appropriate template
        template = self._get_template(review_type)

        # Build few-shot examples
        few_shot = self.templates.FEW_SHOT_EXAMPLES if include_examples else ""

        # Format the prompt
        prompt = template.format(
            code=code.strip(),
            language=language,
            few_shot_examples=few_shot
        )

        # Send to Ollama
        response = self._generate_review(prompt)

        return response

    def _get_template(self, review_type: str) -> str:
        """Get the appropriate prompt template."""
        templates = {
            "general": self.templates.GENERAL_REVIEW,
            "security": self.templates.SECURITY_REVIEW,
            "performance": self.templates.PERFORMANCE_REVIEW,
            "style": self.templates.STYLE_REVIEW,
        }

        return templates.get(review_type, self.templates.GENERAL_REVIEW)

    def _generate_review(self, prompt: str) -> str:
        """Generate review using Ollama."""
        messages = [
            {"role": "system", "content": self.templates.SYSTEM_MESSAGE},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": 4096  # Longer reviews need more tokens
            }
        }

        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

        except httpx.HTTPStatusError as e:
            console.print(f"[red]HTTP Error: {e}[/red]")
            raise
        except httpx.RequestError as e:
            console.print(f"[red]Connection Error: {e}[/red]")
            console.print("[yellow]Is Ollama running? Try: ollama serve[/yellow]")
            raise

    def review_file(
        self,
        file_path: Path,
        review_type: str = "general"
    ) -> str:
        """
        Review code from a file.

        Args:
            file_path: Path to code file
            review_type: Type of review to perform

        Returns:
            Review text
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        code = file_path.read_text()

        # Detect language from extension
        language = self._detect_language(file_path)

        # Perform review
        return self.review_code(code, review_type, language)

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php",
        }

        ext = file_path.suffix.lower()
        return extension_map.get(ext, "text")


def display_review(review_text: str, code: str, language: str = "python"):
    """Display review in a beautiful formatted way."""

    # Show original code
    console.print("\n[bold cyan]📄 Code Under Review:[/bold cyan]\n")
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)

    # Show review
    console.print("\n[bold cyan]📝 Review Results:[/bold cyan]\n")
    console.print(Panel(
        Markdown(review_text),
        border_style="cyan",
        padding=(1, 2)
    ))


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Code Review Assistant - Learn structured prompting"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="File to review"
    )
    parser.add_argument(
        "--code",
        type=str,
        help="Code string to review"
    )
    parser.add_argument(
        "--review-type",
        choices=["general", "security", "performance", "style"],
        default="general",
        help="Type of review to perform"
    )
    parser.add_argument(
        "--language",
        default="python",
        help="Programming language (default: python)"
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model to use"
    )
    parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Disable few-shot examples"
    )

    args = parser.parse_args()

    # Validate input
    if not args.file and not args.code:
        # Read from stdin if no file or code provided
        if not sys.stdin.isatty():
            code = sys.stdin.read()
        else:
            console.print("[red]Error: Provide --file, --code, or pipe code via stdin[/red]")
            parser.print_help()
            sys.exit(1)
    elif args.file:
        code = args.file.read_text()
        args.language = CodeReviewAgent(model=args.model)._detect_language(args.file)
    else:
        code = args.code

    # Create agent
    agent = CodeReviewAgent(model=args.model)

    # Display header
    console.print(Panel.fit(
        f"[bold cyan]Code Review Assistant[/bold cyan]\n\n"
        f"Model: [yellow]{args.model}[/yellow]\n"
        f"Review Type: [yellow]{args.review_type.title()}[/yellow]\n"
        f"Language: [yellow]{args.language}[/yellow]",
        border_style="cyan"
    ))

    # Perform review
    try:
        console.print("\n[dim]Analyzing code...[/dim]\n")

        review = agent.review_code(
            code=code,
            review_type=args.review_type,
            language=args.language,
            include_examples=not args.no_examples
        )

        # Display results
        display_review(review, code, args.language)

    except KeyboardInterrupt:
        console.print("\n[yellow]Review cancelled.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
