#!/usr/bin/env python3
"""
Agent 6: PR Analyzer
====================

Learning Objectives:
- Multi-step reasoning with LangChain
- LCEL (LangChain Expression Language)
- Chain composition
- Structured output parsing

Complexity: ⭐⭐⭐⭐ Advanced
Framework: langchain with LCEL
"""

import sys
from pathlib import Path
from typing import Dict, List

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from git import Repo
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class PRAnalyzer:
    """
    Analyze Pull Requests using multi-step reasoning.

    Demonstrates:
    1. LCEL chain composition
    2. Multi-step analysis
    3. Structured reasoning
    4. Context management
    """

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

        # Step 1: Summarize changes
        self.summary_chain = (
            PromptTemplate.from_template(
                "Summarize these code changes in 2-3 sentences:\n\n{diff}\n\nSummary:"
            )
            | self.llm
            | StrOutputParser()
        )

        # Step 2: Identify risks
        self.risk_chain = (
            PromptTemplate.from_template(
                "Based on this summary:\n{summary}\n\nAnd these changes:\n{diff}\n\n"
                "List potential risks or concerns (security, performance, breaking changes):"
            )
            | self.llm
            | StrOutputParser()
        )

        # Step 3: Generate recommendations
        self.recommendation_chain = (
            PromptTemplate.from_template(
                "Summary: {summary}\n\nRisks: {risks}\n\n"
                "Provide specific recommendations for improving this PR:"
            )
            | self.llm
            | StrOutputParser()
        )

    def analyze_pr(self, diff: str) -> Dict[str, str]:
        """Analyze a PR using multi-step reasoning."""
        console.print("[cyan]Step 1: Summarizing changes...[/cyan]")
        summary = self.summary_chain.invoke({"diff": diff[:2000]})

        console.print("[cyan]Step 2: Identifying risks...[/cyan]")
        risks = self.risk_chain.invoke({"summary": summary, "diff": diff[:2000]})

        console.print("[cyan]Step 3: Generating recommendations...[/cyan]")
        recommendations = self.recommendation_chain.invoke({
            "summary": summary,
            "risks": risks
        })

        return {
            "summary": summary,
            "risks": risks,
            "recommendations": recommendations
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PR Analyzer")
    parser.add_argument("--branch", help="Branch to analyze")
    parser.add_argument("--model", default="qwen2.5-coder:7b")

    args = parser.parse_args()

    try:
        analyzer = PRAnalyzer(model=args.model)

        # Get diff
        repo = Repo(".", search_parent_directories=True)
        if args.branch:
            diff = repo.git.diff(f"origin/main...{args.branch}")
        else:
            diff = repo.git.diff("HEAD~1..HEAD")

        if not diff:
            console.print("[yellow]No changes to analyze[/yellow]")
            sys.exit(0)

        console.print(Panel.fit("[bold cyan]PR Analyzer[/bold cyan]"))

        # Analyze
        results = analyzer.analyze_pr(diff)

        # Display
        console.print("\n[bold green]Summary:[/bold green]")
        console.print(results["summary"])

        console.print("\n[bold yellow]Risks:[/bold yellow]")
        console.print(results["risks"])

        console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        console.print(results["recommendations"])

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
