#!/usr/bin/env python3
"""Agent 27: Code Quality Mentor."""

from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class CodeQualityMentor:
    PRINCIPLES = ["Single Responsibility", "Open/Closed", "Liskov Substitution",
                  "Interface Segregation", "Dependency Inversion"]

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def review_code(self, code: str) -> str:
        """Provide mentorship-style code review."""
        prompt = f"""As a senior engineer mentoring a colleague, review this code:

```python
{code}
```

Provide friendly, constructive feedback on:
1. SOLID principles adherence
2. Code readability
3. Naming conventions
4. Potential bugs
5. Refactoring opportunities
6. What's done well (always start positive!)
7. Learning resources for improvement

Be encouraging and educational.
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Quality Mentor")
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()

    mentor = CodeQualityMentor()
    code = args.file.read_text()
    console.print("[cyan]Reviewing your code...[/cyan]\n")
    review = mentor.review_code(code)
    console.print(review)

if __name__ == "__main__":
    main()
