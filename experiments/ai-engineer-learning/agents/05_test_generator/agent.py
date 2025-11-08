#!/usr/bin/env python3
"""
Agent 5: Test Generator
=======================

Learning Objectives:
- Parse Python code using AST
- Analyze functions and classes
- Generate comprehensive unit tests
- Use LangChain for code generation

Complexity: ⭐⭐⭐ Intermediate-Advanced
Framework: langchain + ast
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    source_code: str


class TestGenerator:
    """
    Generate unit tests from Python code.

    Demonstrates:
    1. AST parsing and code analysis
    2. Structured code generation
    3. LangChain prompt templates
    4. Test framework integration
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        framework: str = "pytest"
    ):
        self.model = model
        self.framework = framework
        self.llm = OllamaLLM(model=model, temperature=0.3)

        self.test_template = PromptTemplate.from_template("""
You are an expert Python developer writing comprehensive unit tests.

Function to test:
```python
{source_code}
```

Function details:
- Name: {function_name}
- Parameters: {parameters}
- Returns: {returns}
{docstring_info}

Generate comprehensive {framework} tests that:
1. Test normal cases
2. Test edge cases (empty inputs, None, etc.)
3. Test error conditions
4. Use meaningful test names
5. Include docstrings
6. Use fixtures if appropriate

Generate ONLY the test code (no explanations):
""")

    def analyze_file(self, file_path: Path) -> List[FunctionInfo]:
        """Parse Python file and extract function information."""
        code = file_path.read_text()
        tree = ast.parse(code)

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue

                func_info = FunctionInfo(
                    name=node.name,
                    args=[arg.arg for arg in node.args.args],
                    returns=ast.unparse(node.returns) if node.returns else None,
                    docstring=ast.get_docstring(node),
                    source_code=ast.unparse(node)
                )
                functions.append(func_info)

        return functions

    def generate_tests(self, func_info: FunctionInfo) -> str:
        """Generate tests for a function."""
        docstring_info = f"- Docstring: {func_info.docstring}" if func_info.docstring else ""

        prompt = self.test_template.format(
            source_code=func_info.source_code,
            function_name=func_info.name,
            parameters=", ".join(func_info.args) if func_info.args else "None",
            returns=func_info.returns or "Unknown",
            docstring_info=docstring_info,
            framework=self.framework
        )

        return self.llm.invoke(prompt)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test Generator")
    parser.add_argument("--file", type=Path, required=True, help="Python file to generate tests for")
    parser.add_argument("--function", help="Specific function to test")
    parser.add_argument("--framework", default="pytest", choices=["pytest", "unittest"], help="Test framework")
    parser.add_argument("--output", type=Path, help="Output file for tests")
    parser.add_argument("--model", default="qwen2.5-coder:7b")

    args = parser.parse_args()

    try:
        generator = TestGenerator(model=args.model, framework=args.framework)

        console.print(Panel.fit(
            f"[bold cyan]Test Generator[/bold cyan]\n\n"
            f"File: [yellow]{args.file}[/yellow]\n"
            f"Framework: [yellow]{args.framework}[/yellow]"
        ))

        # Analyze file
        functions = generator.analyze_file(args.file)

        if not functions:
            console.print("[yellow]No testable functions found[/yellow]")
            sys.exit(0)

        console.print(f"\n[green]Found {len(functions)} functions[/green]")

        # Generate tests
        all_tests = []
        for func in functions:
            if args.function and func.name != args.function:
                continue

            console.print(f"\n[cyan]Generating tests for: {func.name}[/cyan]")
            tests = generator.generate_tests(func)
            all_tests.append(tests)

            console.print(Syntax(tests, "python", theme="monokai"))

        # Save to file if specified
        if args.output and all_tests:
            output_content = "\n\n".join(all_tests)
            args.output.write_text(output_content)
            console.print(f"\n[green]✓ Tests saved to {args.output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
