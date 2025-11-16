"""Embedding providers for RAG system."""

from typing import List, Protocol
from abc import ABC, abstractmethod

import openai
import ollama


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        ...

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        ...


class OpenAIEmbedder:
    """OpenAI embedding provider."""

    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        """Initialize OpenAI embedder.

        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key
        """
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        # TODO: Implement batch embedding with cost tracking
        raise NotImplementedError("OpenAI embedding not yet implemented")

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        # TODO: Implement query embedding
        raise NotImplementedError("Query embedding not yet implemented")


class OllamaEmbedder:
    """Ollama local embedding provider."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434"
    ):
        """Initialize Ollama embedder.

        Args:
            model: Ollama model name
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        # TODO: Implement Ollama batch embedding
        raise NotImplementedError("Ollama embedding not yet implemented")

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        # TODO: Implement Ollama query embedding
        raise NotImplementedError("Ollama query embedding not yet implemented")


def get_embedder(provider: str, **kwargs) -> EmbeddingProvider:
    """Factory function to get embedding provider.

    Args:
        provider: "openai" or "ollama"
        **kwargs: Provider-specific arguments

    Returns:
        EmbeddingProvider instance
    """
    if provider == "openai":
        return OpenAIEmbedder(**kwargs)
    elif provider == "ollama":
        return OllamaEmbedder(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
