#!/usr/bin/env python3
"""
Agent 7: Refactoring Suggester
===============================

Learning Objectives:
- Use vector embeddings for code
- Implement semantic code search
- Detect code duplication
- Suggest refactoring opportunities

Complexity: ⭐⭐⭐⭐ Advanced
Framework: chromadb + ollama embeddings
"""

import sys
from pathlib import Path
from typing import List, Dict

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Error: chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.panel import Panel

console = Console()


class RefactoringSuggester:
    """
    Suggest refactorings using semantic code search.

    Demonstrates:
    1. Code embeddings
    2. Semantic similarity
    3. Duplicate detection
    4. Refactoring suggestions
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        embed_model: str = "nomic-embed-text"
    ):
        self.llm = OllamaLLM(model=model, temperature=0.3)
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="code_patterns",
            embedding_function=embedding_functions.OllamaEmbeddingFunction(
                model_name=embed_model,
                url="http://localhost:11434/api/embeddings"
            )
        )

    def index_codebase(self, source_path: Path):
        """Index Python files in codebase."""
        files = list(source_path.rglob("*.py"))
        console.print(f"[cyan]Indexing {len(files)} files...[/cyan]")

        for i, file_path in enumerate(files):
            try:
                code = file_path.read_text()
                # Split into functions/classes
                chunks = self._split_code(code)

                for j, chunk in enumerate(chunks):
                    self.collection.add(
                        documents=[chunk],
                        ids=[f"{file_path.name}_{i}_{j}"],
                        metadatas=[{"file": str(file_path), "chunk": j}]
                    )
            except Exception as e:
                console.print(f"[yellow]Skipped {file_path}: {e}[/yellow]")

        console.print("[green]✓ Indexing complete[/green]")

    def find_similar_code(self, code_snippet: str, n_results: int = 5) -> List[Dict]:
        """Find similar code patterns."""
        results = self.collection.query(
            query_texts=[code_snippet],
            n_results=n_results
        )

        return [
            {"code": doc, "file": meta["file"]}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]

    def suggest_refactoring(self, code: str) -> str:
        """Suggest refactoring for code."""
        similar = self.find_similar_code(code, n_results=3)

        prompt = f"""Analyze this code and suggest refactorings:

Code to refactor:
```python
{code}
```

Similar patterns found in codebase:
{chr(10).join([f"- {s['file']}" for s in similar])}

Provide:
1. Code smells identified
2. Refactoring suggestions
3. Example refactored code
"""

        return self.llm.invoke(prompt)

    def _split_code(self, code: str) -> List[str]:
        """Simple code splitting (can be improved with AST)."""
        # Simple split by functions/classes
        lines = code.split('\n')
        chunks = []
        current_chunk = []

        for line in lines:
            if line.startswith('def ') or line.startswith('class '):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
            else:
                current_chunk.append(line)

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return [c for c in chunks if len(c.strip()) > 50]  # Filter small chunks


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Refactoring Suggester")
    parser.add_argument("--index", type=Path, help="Index codebase directory")
    parser.add_argument("--code", help="Code to analyze")
    parser.add_argument("--file", type=Path, help="File to analyze")

    args = parser.parse_args()

    try:
        suggester = RefactoringSuggester()

        if args.index:
            suggester.index_codebase(args.index)

        if args.code or args.file:
            code = args.code or args.file.read_text()
            suggestions = suggester.suggest_refactoring(code)
            console.print(Panel(suggestions, title="Refactoring Suggestions", border_style="green"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
