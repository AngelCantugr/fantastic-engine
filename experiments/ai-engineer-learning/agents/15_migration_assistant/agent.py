#!/usr/bin/env python3
"""Agent 15: Migration Assistant - Automate code migrations and framework upgrades."""

import sys
import ast
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class MigrationAssistant:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def migrate_code(self, code: str, from_version: str, to_version: str) -> str:
        """Generate migration plan and transformed code."""
        prompt = f"""Migrate this code from {from_version} to {to_version}:

{code}

Provide:
1. Migration strategy
2. Breaking changes to handle
3. Transformed code
4. Testing recommendations
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migration Assistant")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--from", dest="from_version", required=True)
    parser.add_argument("--to", dest="to_version", required=True)
    args = parser.parse_args()

    assistant = MigrationAssistant()
    code = args.file.read_text()
    console.print(f"[cyan]Migrating from {args.from_version} to {args.to_version}...[/cyan]\n")
    migration = assistant.migrate_code(code, args.from_version, args.to_version)
    console.print(migration)

if __name__ == "__main__":
    main()
