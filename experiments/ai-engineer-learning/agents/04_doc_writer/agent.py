#!/usr/bin/env python3
"""
Agent 4: Documentation Writer (RAG)
====================================

Learning Objectives:
- Understand RAG fundamentals
- Use LlamaIndex for document processing
- Create and query vector stores
- Generate documentation from code

Complexity: ⭐⭐⭐ Intermediate
Framework: llamaindex + chromadb
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Document,
        Settings
    )
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
except ImportError:
    print("Error: llama-index not installed")
    print("Run: pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class DocumentationWriter:
    """
    AI documentation writer using RAG.

    This agent demonstrates:
    1. Document loading and processing
    2. Vector embeddings and search
    3. RAG pattern implementation
    4. Documentation generation from code
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        embed_model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434"
    ):
        """Initialize the documentation writer."""

        # Configure LlamaIndex settings
        Settings.llm = Ollama(model=model, base_url=base_url, temperature=0.3)
        Settings.embed_model = OllamaEmbedding(
            model_name=embed_model,
            base_url=base_url
        )

        self.index: Optional[VectorStoreIndex] = None

    def index_codebase(self, source_path: Path, file_extensions: List[str] = None):
        """
        Index a codebase for documentation generation.

        Args:
            source_path: Path to source code directory
            file_extensions: File extensions to include (default: ['.py', '.js', '.ts'])
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.md']

        console.print(f"\n[cyan]Indexing codebase: {source_path}[/cyan]")

        # Load documents
        documents = []
        for ext in file_extensions:
            files = list(source_path.rglob(f"*{ext}"))
            console.print(f"Found {len(files)} {ext} files")

            for file_path in files:
                try:
                    content = file_path.read_text()
                    doc = Document(
                        text=content,
                        metadata={"file_path": str(file_path), "type": ext}
                    )
                    documents.append(doc)
                except Exception as e:
                    console.print(f"[yellow]Skipped {file_path}: {e}[/yellow]")

        console.print(f"\n[green]Loaded {len(documents)} documents[/green]")

        # Create index
        console.print("[cyan]Creating vector index...[/cyan]")
        self.index = VectorStoreIndex.from_documents(documents)
        console.print("[green]✓ Index created[/green]\n")

    def generate_documentation(self, query: str) -> str:
        """Generate documentation based on a query."""
        if not self.index:
            raise ValueError("No codebase indexed. Call index_codebase() first.")

        query_engine = self.index.as_query_engine(similarity_top_k=3)
        response = query_engine.query(query)

        return str(response)

    def explain_code(self, code: str) -> str:
        """Explain a code snippet."""
        doc = Document(text=code)
        index = VectorStoreIndex.from_documents([doc])
        query_engine = index.as_query_engine()

        response = query_engine.query(
            "Explain this code in detail. Include what it does, how it works, "
            "and any important concepts. Format as markdown."
        )

        return str(response)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation Writer with RAG")
    parser.add_argument("--source", type=Path, help="Source code directory to index")
    parser.add_argument("--query", type=str, help="Query to generate documentation")
    parser.add_argument("--code", type=str, help="Code snippet to explain")
    parser.add_argument("--model", default="qwen2.5-coder:7b", help="LLM model")
    parser.add_argument("--embed-model", default="nomic-embed-text", help="Embedding model")

    args = parser.parse_args()

    try:
        writer = DocumentationWriter(model=args.model, embed_model=args.embed_model)

        if args.code:
            # Explain code snippet
            console.print(Panel.fit("[bold cyan]Code Explanation[/bold cyan]"))
            explanation = writer.explain_code(args.code)
            console.print(Markdown(explanation))

        elif args.source and args.query:
            # Index and query codebase
            writer.index_codebase(args.source)
            response = writer.generate_documentation(args.query)
            console.print(Panel(Markdown(response), title="Documentation", border_style="green"))

        else:
            console.print("[red]Provide --code or (--source and --query)[/red]")
            parser.print_help()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
