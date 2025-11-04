"""
Interactive RAG - See What's Happening Under the Hood

This version shows you what the RAG system is doing:
- Which chunks were retrieved
- Similarity scores
- The actual prompt sent to the LLM
- Token counts

Perfect for understanding how RAG works in practice!
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()


class InteractiveRAG:
    """RAG system with detailed visibility into operations."""

    def __init__(self, data_dir: str = "../data", use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.data_dir = data_dir
        self.vector_store = None
        self.llm = None
        self.embeddings = None

        self._setup()

    def _setup(self):
        """Initialize all components."""
        console.print(Panel("🔧 Initializing Interactive RAG System", style="bold cyan"))

        # 1. Setup embeddings
        if self.use_ollama:
            console.print("Using Ollama embeddings (local)")
            self.embeddings = OllamaEmbeddings(model="llama2")
        else:
            console.print("Using OpenAI embeddings")
            self.embeddings = OpenAIEmbeddings()

        # 2. Setup LLM
        if self.use_ollama:
            console.print("Using Ollama LLM (local)")
            self.llm = Ollama(model="llama2", temperature=0)
        else:
            console.print("Using OpenAI GPT-3.5")
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # 3. Load and process documents
        self._load_documents()

        console.print("[green]✅ RAG system ready![/green]\n")

    def _load_documents(self):
        """Load documents and create vector store."""
        current_dir = Path(__file__).parent
        data_path = (current_dir / self.data_dir).resolve()

        console.print(f"📂 Loading documents from: {data_path}")

        # Load documents
        loader = DirectoryLoader(
            str(data_path),
            glob="*.txt",
            loader_cls=TextLoader,
            show_progress=False
        )
        documents = loader.load()

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)

        console.print(f"📄 Loaded {len(documents)} documents → {len(chunks)} chunks")

        # Create vector store
        console.print("🔨 Building vector database...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="interactive_rag"
        )

    def search_similar_chunks(self, query: str, k: int = 3):
        """
        Retrieve similar chunks with similarity scores.

        This shows you exactly what the RAG system retrieves!
        """
        console.print(Panel(
            f"[bold]Query:[/bold] {query}",
            title="🔍 Searching",
            border_style="cyan"
        ))

        # Search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)

        # Display results in a table
        table = Table(title=f"Top {k} Retrieved Chunks", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Source", style="cyan", width=25)
        table.add_column("Similarity", justify="right", style="green", width=10)
        table.add_column("Preview", width=50)

        for i, (doc, score) in enumerate(results, 1):
            filename = Path(doc.metadata['source']).name
            # Lower score = more similar in some distance metrics
            # Convert to percentage for clarity
            similarity_pct = f"{(1 - score) * 100:.1f}%"
            preview = doc.page_content[:100].replace("\n", " ") + "..."

            table.add_row(
                str(i),
                filename,
                similarity_pct,
                preview
            )

        console.print(table)

        return results

    def generate_answer(self, query: str, k: int = 3):
        """
        Generate answer with full visibility into the process.

        Shows:
        - Retrieved chunks
        - Constructed prompt
        - LLM response
        """
        console.print("\n" + "="*80)
        console.print("[bold yellow]Question:[/bold yellow]", query)
        console.print("="*80 + "\n")

        # Step 1: Retrieve similar chunks
        results = self.search_similar_chunks(query, k=k)
        docs = [doc for doc, score in results]

        # Step 2: Construct context from retrieved chunks
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])

        # Show context length
        context_words = len(context.split())
        console.print(f"\n📊 [dim]Context length: {context_words} words[/dim]")

        # Step 3: Create prompt
        prompt_template = """You are a helpful AI assistant. Answer the question based on the provided context.
If you cannot answer from the context, say so.

Context:
{context}

Question: {question}

Answer:"""

        full_prompt = prompt_template.format(context=context, question=query)

        # Show the prompt (truncated)
        console.print("\n" + Panel(
            full_prompt[:500] + "\n\n[dim]... (truncated) ...[/dim]",
            title="📝 Prompt Sent to LLM",
            border_style="yellow",
            expand=False
        ))

        # Step 4: Get LLM response
        console.print("\n🤖 [dim]Generating answer...[/dim]")

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        answer = chain.run(context=context, question=query)

        # Step 5: Display answer
        console.print("\n" + Panel(
            Markdown(answer),
            title="✨ Answer",
            border_style="green"
        ))

        # Step 6: Show sources
        console.print("\n[bold cyan]📚 Information Sources:[/bold cyan]")
        for i, doc in enumerate(docs, 1):
            filename = Path(doc.metadata['source']).name
            console.print(f"\n{i}. {filename}")
            snippet = doc.page_content[:200].replace("\n", " ")
            console.print(f"   [dim]{snippet}...[/dim]")

        return answer

    def compare_queries(self, query1: str, query2: str):
        """
        Compare how different queries retrieve different chunks.

        Educational: Shows how query formulation affects retrieval!
        """
        console.print(Panel(
            "Comparing Query Formulations",
            style="bold magenta"
        ))

        console.print(f"\n[bold]Query 1:[/bold] {query1}")
        results1 = self.vector_store.similarity_search_with_score(query1, k=3)

        console.print(f"\n[bold]Query 2:[/bold] {query2}")
        results2 = self.vector_store.similarity_search_with_score(query2, k=3)

        # Compare overlaps
        docs1 = set([Path(doc.metadata['source']).name for doc, _ in results1])
        docs2 = set([Path(doc.metadata['source']).name for doc, _ in results2])

        overlap = docs1 & docs2
        unique1 = docs1 - docs2
        unique2 = docs2 - docs1

        console.print("\n[bold]Retrieval Comparison:[/bold]")
        console.print(f"  Common sources: {len(overlap)} - {overlap}")
        console.print(f"  Unique to Query 1: {len(unique1)} - {unique1}")
        console.print(f"  Unique to Query 2: {len(unique2)} - {unique2}")

        console.print("\n💡 [yellow]Learning:[/yellow] Different queries can retrieve different context!")


def main():
    """Interactive demo of RAG system."""
    load_dotenv()

    console.print(Panel.fit(
        "[bold magenta]Interactive RAG System[/bold magenta]\n"
        "See what's happening under the hood!",
        border_style="magenta"
    ))

    use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"

    # Initialize RAG system
    rag = InteractiveRAG(use_ollama=use_ollama)

    # Demo mode: Show different features
    console.print("\n[bold cyan]🎓 Demo Mode[/bold cyan]")
    console.print("Let's explore how RAG works!\n")

    # Example 1: Basic question
    console.print(Panel("Example 1: Basic Question", style="bold yellow"))
    rag.generate_answer("What is machine learning?", k=3)

    input("\n[Press Enter to continue...]")

    # Example 2: Show how query formulation matters
    console.print("\n" + Panel("Example 2: Query Formulation", style="bold yellow"))
    rag.compare_queries(
        "What is machine learning?",
        "Explain supervised vs unsupervised learning"
    )

    input("\n[Press Enter to continue...]")

    # Example 3: Question requiring multiple sources
    console.print("\n" + Panel("Example 3: Multi-Source Question", style="bold yellow"))
    rag.generate_answer(
        "How do embeddings relate to machine learning and NLP?",
        k=5  # Retrieve more chunks
    )

    # Interactive mode
    console.print("\n" + "="*80)
    console.print("[bold green]🎮 Interactive Mode[/bold green]")
    console.print("Type your questions or commands:")
    console.print("  • Any question → Get an answer")
    console.print("  • 'search: <query>' → Just search, don't generate")
    console.print("  • 'compare' → Compare two queries")
    console.print("  • 'quit' → Exit")
    console.print("="*80 + "\n")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            if user_input.lower().startswith('search:'):
                query = user_input[7:].strip()
                rag.search_similar_chunks(query, k=3)

            elif user_input.lower() == 'compare':
                query1 = input("Query 1: ").strip()
                query2 = input("Query 2: ").strip()
                rag.compare_queries(query1, query2)

            else:
                # Generate answer
                rag.generate_answer(user_input)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    console.print("\n[bold green]Thanks for exploring RAG! 🚀[/bold green]")


if __name__ == "__main__":
    main()
