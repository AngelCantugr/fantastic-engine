#!/usr/bin/env python3
"""Agent 30: Interactive Debugger - Master debugging skills."""

from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class InteractiveDebugger:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def debug_session(self, code: str, error: str = None):
        """Interactive debugging session."""
        console.print("[bold cyan]Interactive Debugging Session[/bold cyan]\n")

        if error:
            console.print(f"[red]Error:[/red] {error}\n")

        console.print("[yellow]Let's debug together. What have you tried so far?[/yellow]")
        attempts = Prompt.ask("Your debugging attempts")

        guidance = self._get_debugging_guidance(code, error, attempts)
        console.print(f"\n[cyan]Debugging Guide:[/cyan]\n{guidance}")

        console.print("\n[yellow]Based on this guidance, what would you try next?[/yellow]")
        next_step = Prompt.ask("Your next step")

        feedback = self._provide_feedback(next_step, code, error)
        console.print(f"\n{feedback}")

    def _get_debugging_guidance(self, code: str, error: str, attempts: str) -> str:
        prompt = f"""Guide a developer through debugging this code:

Code:
```python
{code}
```

{f"Error: {error}" if error else ""}

What they've tried: {attempts}

Provide:
1. Root cause hypothesis
2. Debugging strategy (divide & conquer, rubber duck, etc.)
3. Specific questions to investigate
4. Tools to use (print, debugger, logging)
5. Step-by-step debugging plan
6. Common pitfalls in similar situations

Be Socratic - guide them to the solution rather than giving it away.
"""
        return self.llm.invoke(prompt)

    def _provide_feedback(self, next_step: str, code: str, error: str) -> str:
        prompt = f"""Evaluate this debugging approach:

Proposed next step: {next_step}

For the code with issue: {error}

Provide:
1. Is this a good next step? Why or why not?
2. Alternative approaches
3. What they might discover from this step
4. Follow-up questions to consider
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Interactive Debugger")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--error", type=str, help="Error message")
    args = parser.parse_args()

    debugger = InteractiveDebugger()
    code = args.file.read_text()
    debugger.debug_session(code, args.error)

if __name__ == "__main__":
    main()
