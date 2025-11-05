"""
Basic RAG Implementation - Learning Edition

This is the simplest possible RAG implementation, designed to help you understand
each step of the process. We use extensive comments to explain what's happening.

RAG Steps:
1. Load documents
2. Split documents into chunks
3. Create embeddings for chunks
4. Store embeddings in vector database
5. Query: Embed question → Find similar chunks → Generate answer with LLM
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports for RAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# For embeddings and LLMs, we support both Ollama (local) and OpenAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Rich console for beautiful terminal output
console = Console()


def print_step(step_number: int, title: str, description: str):
    """Pretty print each step of the RAG process."""
    console.print(f"\n[bold cyan]Step {step_number}: {title}[/bold cyan]")
    console.print(f"[dim]{description}[/dim]")


def load_documents(data_dir: str = "../data"):
    """
    Step 1: Load Documents

    Load all text files from the data directory. Each file becomes a Document object
    with content and metadata (like filename).

    Think of this as gathering all the books you'll reference for your open-book exam.
    """
    print_step(
        1,
        "Loading Documents",
        "Reading all .txt files from the data directory"
    )

    # Get absolute path to data directory
    current_dir = Path(__file__).parent
    data_path = (current_dir / data_dir).resolve()

    console.print(f"📂 Loading from: {data_path}")

    # DirectoryLoader loads all matching files
    loader = DirectoryLoader(
        str(data_path),
        glob="*.txt",  # Only .txt files
        loader_cls=TextLoader,  # Use TextLoader for each file
        show_progress=True
    )

    documents = loader.load()
    console.print(f"✅ Loaded {len(documents)} documents")

    # Show what we loaded
    for doc in documents:
        filename = Path(doc.metadata['source']).name
        word_count = len(doc.page_content.split())
        console.print(f"  📄 {filename}: {word_count} words")

    return documents


def split_documents(documents):
    """
    Step 2: Split Documents into Chunks

    Why split? Because:
    1. LLMs have limited context windows
    2. Smaller chunks = more precise retrieval
    3. Each chunk can be independently relevant

    We use RecursiveCharacterTextSplitter which tries to split on:
    - Paragraphs first (double newline)
    - Then sentences
    - Then words
    - Finally characters (if needed)
    """
    print_step(
        2,
        "Splitting Documents",
        "Breaking documents into manageable chunks with overlap"
    )

    # Initialize the splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # ~125 words, ~500 characters
        chunk_overlap=50,  # Overlap to preserve context between chunks
        length_function=len,  # Use character count
        separators=["\n\n", "\n", " ", ""]  # Split priority
    )

    console.print("⚙️  Chunk size: 500 characters")
    console.print("⚙️  Chunk overlap: 50 characters")
    console.print("⚙️  This helps preserve context across chunk boundaries")

    chunks = text_splitter.split_documents(documents)

    console.print(f"✅ Created {len(chunks)} chunks")

    # Show example chunk
    if chunks:
        console.print("\n[bold]Example chunk:[/bold]")
        example = chunks[0].page_content[:200] + "..."
        console.print(Panel(example, title="Chunk 0", border_style="cyan"))

    return chunks


def create_vector_store(chunks, use_ollama=True):
    """
    Step 3: Create Embeddings and Vector Store

    This is where the magic happens!

    1. Embedding Model converts each chunk into a vector (list of numbers)
    2. Vector Database (ChromaDB) stores these vectors
    3. Similar chunks have similar vectors (measured by cosine similarity)

    It's like creating an index for a book, but way more powerful because
    it understands semantic meaning, not just keywords!
    """
    print_step(
        3,
        "Creating Embeddings & Vector Store",
        "Converting text chunks into numerical vectors for similarity search"
    )

    # Choose embedding model based on configuration
    if use_ollama:
        console.print("🤖 Using Ollama embeddings (local, free)")
        embeddings = OllamaEmbeddings(
            model="llama2",  # Can also use "mistral", "neural-chat", etc.
        )
    else:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not installed. Run: pip install openai langchain-openai")
        console.print("🌐 Using OpenAI embeddings (requires API key)")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # Fast and cost-effective
        )

    console.print("📊 Creating vector database (this may take a moment)...")

    # Create Chroma vector store
    # This will:
    # 1. Convert each chunk to an embedding
    # 2. Store embeddings in a local database
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="rag_learning",
        persist_directory="./chroma_db"  # Save to disk
    )

    console.print(f"✅ Vector store created with {len(chunks)} embeddings")
    console.print("💾 Saved to: ./chroma_db")

    return vector_store


def create_qa_chain(vector_store, use_ollama=True):
    """
    Step 4: Create the QA Chain

    The QA Chain orchestrates the RAG process:
    1. Takes your question
    2. Converts question to embedding
    3. Finds most similar chunks (retrieval)
    4. Constructs a prompt with question + chunks
    5. Sends to LLM for answer generation

    LangChain handles all this complexity for us!
    """
    print_step(
        4,
        "Setting Up QA Chain",
        "Creating the retrieval + generation pipeline"
    )

    # Choose LLM based on configuration
    if use_ollama:
        console.print("🤖 Using Ollama LLM (local, free)")
        llm = Ollama(
            model="llama2",
            temperature=0,  # Deterministic responses
        )
    else:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not installed. Run: pip install openai langchain-openai")
        console.print("🌐 Using OpenAI GPT-3.5")
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
        )

    # Create retriever from vector store
    # k=3 means retrieve top 3 most similar chunks
    retriever = vector_store.as_retriever(
        search_type="similarity",  # Use cosine similarity
        search_kwargs={"k": 3}  # Return top 3 chunks
    )

    console.print("⚙️  Retrieval strategy: Similarity search")
    console.print("⚙️  Number of chunks to retrieve: 3")

    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # "stuff" = put all retrieved chunks into prompt
        retriever=retriever,
        return_source_documents=True,  # Return sources for transparency
        verbose=False
    )

    console.print("✅ QA Chain ready!")

    return qa_chain


def ask_question(qa_chain, question: str):
    """
    Step 5: Ask Questions!

    Now we can ask questions and get answers grounded in our documents.

    Behind the scenes:
    1. Question → Embedding
    2. Find similar chunks using vector similarity
    3. Construct prompt: "Based on these documents, answer this question"
    4. LLM generates answer
    """
    print_step(
        5,
        f"Asking Question",
        "Retrieving relevant context and generating answer"
    )

    console.print(f"\n[bold yellow]Question:[/bold yellow] {question}\n")

    # Run the QA chain
    result = qa_chain({"query": question})

    # Display answer
    answer = result['result']
    console.print("[bold green]Answer:[/bold green]")
    console.print(Markdown(answer))

    # Show source documents for transparency
    console.print("\n[bold cyan]📚 Sources Used:[/bold cyan]")
    for i, doc in enumerate(result['source_documents'], 1):
        filename = Path(doc.metadata['source']).name
        snippet = doc.page_content[:150].replace("\n", " ") + "..."
        console.print(f"\n{i}. [dim]{filename}[/dim]")
        console.print(f"   {snippet}")

    return result


def main():
    """Main function to run the basic RAG example."""

    console.print(Panel.fit(
        "[bold magenta]Basic RAG Implementation[/bold magenta]\n"
        "Learn how Retrieval-Augmented Generation works!",
        border_style="magenta"
    ))

    # Load environment variables
    load_dotenv()

    # Check configuration
    use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"

    if use_ollama:
        console.print("\n[yellow]Using Ollama (local)[/yellow]")
        console.print("Make sure Ollama is running: ollama serve")
    else:
        console.print("\n[yellow]Using OpenAI[/yellow]")
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]ERROR: OPENAI_API_KEY not set![/red]")
            return

    try:
        # Step 1: Load documents
        documents = load_documents()

        # Step 2: Split into chunks
        chunks = split_documents(documents)

        # Step 3: Create vector store
        vector_store = create_vector_store(chunks, use_ollama=use_ollama)

        # Step 4: Create QA chain
        qa_chain = create_qa_chain(vector_store, use_ollama=use_ollama)

        # Step 5: Ask some questions!
        console.print("\n" + "="*70)
        console.print("[bold]Now let's ask some questions![/bold]")
        console.print("="*70)

        # Example questions
        questions = [
            "What is the history of artificial intelligence?",
            "Explain what embeddings are and why they're important.",
            "What are the main types of machine learning?"
        ]

        for i, question in enumerate(questions, 1):
            if i > 1:
                input("\n[Press Enter to ask next question...]")
            ask_question(qa_chain, question)

        # Interactive mode
        console.print("\n" + "="*70)
        console.print("[bold green]Try your own questions![/bold green]")
        console.print("Type 'quit' to exit")
        console.print("="*70 + "\n")

        while True:
            question = input("Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if question:
                ask_question(qa_chain, question)

        console.print("\n[bold green]Thanks for learning about RAG! 🎉[/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    main()
