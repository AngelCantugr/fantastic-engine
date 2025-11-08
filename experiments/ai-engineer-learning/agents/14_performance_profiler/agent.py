#!/usr/bin/env python3
"""Agent 14: Performance Profiler - Analyze and optimize application performance."""

import sys
import cProfile
import pstats
import io
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class PerformanceProfiler:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def profile_code(self, code_file: Path) -> str:
        """Profile Python code and analyze results."""
        profiler = cProfile.Profile()

        # Execute and profile
        code = code_file.read_text()
        profiler.enable()
        try:
            exec(code)
        except Exception as e:
            console.print(f"[yellow]Execution error: {e}[/yellow]")
        profiler.disable()

        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)
        profile_output = s.getvalue()

        # Analyze with LLM
        prompt = f"""Analyze this profiling data and suggest optimizations:

{profile_output}

Provide:
1. Top 3 bottlenecks
2. Specific optimization suggestions
3. Expected performance improvements
4. Code examples for improvements
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Performance Profiler")
    parser.add_argument("--file", type=Path, required=True, help="Python file to profile")
    args = parser.parse_args()

    profiler = PerformanceProfiler()
    console.print("[cyan]Profiling code...[/cyan]\n")
    analysis = profiler.profile_code(args.file)
    console.print(analysis)

if __name__ == "__main__":
    main()
