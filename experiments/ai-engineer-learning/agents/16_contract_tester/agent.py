#!/usr/bin/env python3
"""Agent 16: API Contract Tester - Generate and verify API contract tests."""

import sys
import json
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class ContractTester:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def generate_contract_tests(self, openapi_spec: dict) -> str:
        """Generate contract tests from OpenAPI spec."""
        prompt = f"""Generate contract tests for this API spec:

{json.dumps(openapi_spec, indent=2)}

Generate Python tests using pytest that verify:
1. Request/response schemas
2. Status codes
3. Headers
4. Error conditions

Provide complete test code.
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="API Contract Tester")
    parser.add_argument("--spec", type=Path, required=True, help="OpenAPI spec file")
    parser.add_argument("--output", type=Path, help="Output test file")
    args = parser.parse_args()

    tester = ContractTester()
    spec = json.loads(args.spec.read_text())

    console.print("[cyan]Generating contract tests...[/cyan]\n")
    tests = tester.generate_contract_tests(spec)

    if args.output:
        args.output.write_text(tests)
        console.print(f"[green]✓ Tests saved to {args.output}[/green]")
    else:
        console.print(tests)

if __name__ == "__main__":
    main()
