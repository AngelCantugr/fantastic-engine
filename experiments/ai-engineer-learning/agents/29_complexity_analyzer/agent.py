#!/usr/bin/env python3
"""Agent 29: Complexity Analyzer."""

import ast
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class ComplexityAnalyzer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def analyze_complexity(self, code: str) -> str:
        """Analyze time and space complexity."""
        prompt = f"""Analyze the complexity of this code:

```python
{code}
```

Provide:
1. Time Complexity: O(?) with detailed explanation
2. Space Complexity: O(?) with explanation
3. Best/Average/Worst case analysis
4. Line-by-line complexity breakdown
5. Optimization opportunities
6. Comparison with alternative approaches
7. When this complexity is acceptable vs when to optimize
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Complexity Analyzer")
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()

    analyzer = ComplexityAnalyzer()
    code = args.file.read_text()
    console.print("[cyan]Analyzing complexity...[/cyan]\n")
    analysis = analyzer.analyze_complexity(code)
    console.print(analysis)

if __name__ == "__main__":
    main()
