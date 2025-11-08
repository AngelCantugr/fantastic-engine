"""
Production-Ready RAG System
Implements hybrid retrieval, re-ranking, and comprehensive evaluation.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import tiktoken

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
import numpy as np


@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    chunk_size: int = 1024
    chunk_overlap: int = 256
    top_k: int = 5
    embedding_model: str = "text-embedding-3-large"
    llm_model: str = "gpt-4"
    temperature: float = 0.0
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    dense_weight: float = 0.7  # Weight for dense retrieval in fusion
    sparse_weight: float = 0.3  # Weight for sparse retrieval in fusion


@dataclass
class RAGResult:
    """Result from RAG query"""
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str
    tokens_used: int
    cost: float
    latency: float


class HybridRetriever:
    """Combines dense (vector) and sparse (BM25) retrieval"""

    def __init__(self, vectorstore: Chroma, documents: List[Document], config: RAGConfig):
        self.vectorstore = vectorstore
        self.config = config

        # Build BM25 index
        self.documents = documents
        tokenized_docs = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """Hybrid retrieval with RRF (Reciprocal Rank Fusion)"""

        # Dense retrieval (vector search)
        dense_results = self.vectorstore.similarity_search_with_score(
            query, k=top_k * 2
        )

        # Sparse retrieval (BM25)
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:top_k * 2]

        # Reciprocal Rank Fusion
        k = 60  # RRF constant
        doc_scores = {}

        # Add dense scores
        for rank, (doc, score) in enumerate(dense_results, 1):
            doc_id = doc.page_content
            rrf_score = 1 / (k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (
                self.config.dense_weight * rrf_score
            )

        # Add sparse scores
        for rank, idx in enumerate(top_bm25_indices, 1):
            doc = self.documents[idx]
            doc_id = doc.page_content
            rrf_score = 1 / (k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (
                self.config.sparse_weight * rrf_score
            )

        # Sort by combined score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top k documents
        result_docs = []
        for doc_content, score in sorted_docs[:top_k]:
            # Find the original document
            for doc in self.documents:
                if doc.page_content == doc_content:
                    result_docs.append(doc)
                    break

        return result_docs


class ProductionRAG:
    """Production-ready RAG system with hybrid retrieval and re-ranking"""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()

        # Initialize components
        self.embeddings = OpenAIEmbeddings(
            model=self.config.embedding_model
        )
        self.llm = ChatOpenAI(
            model=self.config.llm_model,
            temperature=self.config.temperature
        )

        # Re-ranker
        self.reranker = CrossEncoder(self.config.rerank_model)

        # Token counter
        self.encoding = tiktoken.encoding_for_model(self.config.llm_model)

        # Storage
        self.vectorstore: Optional[Chroma] = None
        self.documents: List[Document] = []
        self.hybrid_retriever: Optional[HybridRetriever] = None

    def index_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """Index documents for retrieval"""

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Create documents
        self.documents = []
        for i, text in enumerate(texts):
            chunks = text_splitter.split_text(text)
            for j, chunk in enumerate(chunks):
                metadata = metadatas[i] if metadatas else {}
                metadata.update({
                    "source_index": i,
                    "chunk_index": j,
                    "chunk_id": f"{i}_{j}"
                })
                self.documents.append(
                    Document(page_content=chunk, metadata=metadata)
                )

        # Create vector store
        self.vectorstore = Chroma.from_documents(
            self.documents,
            self.embeddings,
            collection_name="production_rag"
        )

        # Initialize hybrid retriever
        self.hybrid_retriever = HybridRetriever(
            self.vectorstore,
            self.documents,
            self.config
        )

        print(f"Indexed {len(self.documents)} chunks from {len(texts)} documents")

    def _rerank(self, query: str, documents: List[Document]) -> List[Document]:
        """Re-rank documents using cross-encoder"""
        if not documents:
            return documents

        # Create pairs for re-ranking
        pairs = [[query, doc.page_content] for doc in documents]

        # Score pairs
        scores = self.reranker.predict(pairs)

        # Sort by score
        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, score in doc_scores]

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD"""
        # GPT-4 pricing (as of 2025)
        input_cost_per_1m = 30.0
        output_cost_per_1m = 60.0

        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m

        return input_cost + output_cost

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
        include_sources: bool = True
    ) -> RAGResult:
        """Query the RAG system"""
        import time
        start_time = time.time()

        if not self.hybrid_retriever:
            raise ValueError("No documents indexed. Call index_documents first.")

        top_k = top_k or self.config.top_k

        # 1. Hybrid Retrieval
        retrieved_docs = self.hybrid_retriever.retrieve(question, top_k=top_k * 2)

        # Apply metadata filters if provided
        if filters:
            retrieved_docs = [
                doc for doc in retrieved_docs
                if all(doc.metadata.get(k) == v for k, v in filters.items())
            ]

        # 2. Re-ranking
        reranked_docs = self._rerank(question, retrieved_docs)[:top_k]

        # 3. Build context
        context_parts = []
        sources = []

        for i, doc in enumerate(reranked_docs, 1):
            context_parts.append(f"[{i}] {doc.page_content}")
            if include_sources:
                sources.append({
                    "index": i,
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                })

        context = "\n\n".join(context_parts)

        # 4. Generate answer
        prompt = f"""Use the following context to answer the question.
If you use information from the context, cite the source using [number].

Context:
{context}

Question: {question}

Answer:"""

        # Count tokens
        input_tokens = self._count_tokens(prompt)

        # Generate
        response = self.llm.predict(prompt)

        output_tokens = self._count_tokens(response)
        total_tokens = input_tokens + output_tokens

        # Calculate cost and latency
        cost = self._estimate_cost(input_tokens, output_tokens)
        latency = time.time() - start_time

        return RAGResult(
            answer=response,
            sources=sources,
            context_used=context,
            tokens_used=total_tokens,
            cost=cost,
            latency=latency
        )

    async def query_async(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
        include_sources: bool = True
    ) -> RAGResult:
        """Async version of query"""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.query(question, top_k, filters, include_sources)
        )


def main():
    """Example usage"""

    # Sample documents about AI technologies
    documents = [
        """
        Model Context Protocol (MCP) is an open protocol by Anthropic that
        standardizes how AI assistants connect to data sources. It's like USB-C
        for AI applications, providing a universal way to integrate tools,
        databases, and systems. MCP uses JSON-RPC 2.0 for communication and
        supports resources (read-only data), tools (executable functions),
        and prompts (reusable templates).
        """,
        """
        RAG (Retrieval-Augmented Generation) combines large language models
        with information retrieval. It works by: 1) Retrieving relevant
        documents from a knowledge base, 2) Augmenting the prompt with
        retrieved context, 3) Generating a response grounded in the context.
        This reduces hallucinations and enables LLMs to access up-to-date
        information without retraining.
        """,
        """
        LangGraph is a framework for building stateful multi-agent applications.
        Unlike traditional chains, LangGraph models workflows as directed graphs
        where nodes are functions and edges control flow. It supports cyclic
        graphs, conditional edges, and persistence. This makes it ideal for
        complex agent workflows that need loops, human-in-the-loop, or
        sophisticated decision trees.
        """,
        """
        CrewAI is a framework for orchestrating role-playing AI agents. You
        define agents with specific roles, goals, and backstories, then assign
        them tasks to complete. Agents can work sequentially (pipeline) or
        hierarchically (manager-workers). CrewAI excels at business processes
        like content creation, research, and customer support where you want
        specialized agent teams.
        """
    ]

    # Initialize RAG system
    print("Initializing RAG system...")
    rag = ProductionRAG()

    # Index documents
    print("\nIndexing documents...")
    rag.index_documents(documents, metadatas=[
        {"topic": "protocols", "source": "mcp_docs"},
        {"topic": "architectures", "source": "rag_guide"},
        {"topic": "frameworks", "source": "langgraph_docs"},
        {"topic": "frameworks", "source": "crewai_docs"}
    ])

    # Query 1: Basic question
    print("\n" + "="*60)
    print("Query 1: What is MCP?")
    print("="*60)

    result = rag.query("What is MCP and how does it work?")

    print(f"\nAnswer:\n{result.answer}")
    print(f"\nMetrics:")
    print(f"  - Tokens: {result.tokens_used}")
    print(f"  - Cost: ${result.cost:.4f}")
    print(f"  - Latency: {result.latency:.2f}s")
    print(f"\nSources: {len(result.sources)}")
    for source in result.sources:
        print(f"  [{source['index']}] {source['content'][:100]}...")

    # Query 2: Comparison question
    print("\n" + "="*60)
    print("Query 2: Compare frameworks")
    print("="*60)

    result = rag.query(
        "What's the difference between LangGraph and CrewAI?",
        top_k=3
    )

    print(f"\nAnswer:\n{result.answer}")
    print(f"\nCost: ${result.cost:.4f} | Latency: {result.latency:.2f}s")

    # Query 3: With filters
    print("\n" + "="*60)
    print("Query 3: Filtered search")
    print("="*60)

    result = rag.query(
        "Tell me about frameworks",
        filters={"topic": "frameworks"}
    )

    print(f"\nAnswer:\n{result.answer}")
    print(f"\nSources (filtered by topic='frameworks'):")
    for source in result.sources:
        print(f"  [{source['index']}] Topic: {source['metadata']['topic']}")


if __name__ == "__main__":
    # Set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-key-here"

    main()
