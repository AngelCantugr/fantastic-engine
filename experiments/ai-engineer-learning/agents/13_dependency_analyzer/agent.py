#!/usr/bin/env python3
"""Agent 13: Dependency Analyzer - Scan dependencies for vulnerabilities and updates."""

import sys
import subprocess
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class DependencyAnalyzer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def scan_requirements(self, requirements_file: Path) -> str:
        """Scan requirements file for vulnerabilities."""
        try:
            # Try pip-audit first
            result = subprocess.run(
                ["pip-audit", "-r", str(requirements_file)],
                capture_output=True, text=True, timeout=30
            )
            audit_output = result.stdout + result.stderr
        except (FileNotFoundError, subprocess.TimeoutExpired):
            audit_output = "pip-audit not available (run: pip install pip-audit)"

        # Analyze with LLM
        prompt = f"""Analyze these dependency scan results:

{audit_output}

Provide:
1. Critical vulnerabilities to fix immediately
2. Recommended version updates
3. Migration strategy
4. License compliance notes
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dependency Analyzer")
    parser.add_argument("--requirements", type=Path, default="requirements.txt")
    args = parser.parse_args()

    analyzer = DependencyAnalyzer()
    console.print("[cyan]Scanning dependencies...[/cyan]\n")
    analysis = analyzer.scan_requirements(args.requirements)
    console.print(analysis)

if __name__ == "__main__":
    main()
