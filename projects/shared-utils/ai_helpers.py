"""AI integration helpers for OpenAI and Ollama."""

import os
from typing import Optional, List, Dict, Any
from enum import Enum

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import ollama
except ImportError:
    ollama = None


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"


class AIHelper:
    """Helper class for AI operations with fallback support."""

    def __init__(
        self,
        provider: ModelProvider = ModelProvider.OPENAI,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if provider == ModelProvider.OPENAI:
            self.model = model or "gpt-4-turbo-preview"
            self.client = self._get_openai_client()
        else:
            self.model = model or "llama3"
            self.client = None  # Ollama uses module-level functions

    def _get_openai_client(self) -> Optional[Any]:
        """Get OpenAI client instance."""
        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        return OpenAI(api_key=self.api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Send a chat completion request."""
        if self.provider == ModelProvider.OPENAI:
            return self._chat_openai(messages, temperature, max_tokens, **kwargs)
        else:
            return self._chat_ollama(messages, temperature, **kwargs)

    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Chat with OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        **kwargs
    ) -> str:
        """Chat with Ollama."""
        if ollama is None:
            raise ImportError("Ollama package not installed. Run: pip install ollama")

        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": temperature},
        )
        return response['message']['content']

    def embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        if self.provider == ModelProvider.OPENAI:
            return self._embeddings_openai(text)
        else:
            return self._embeddings_ollama(text)

    def _embeddings_openai(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _embeddings_ollama(self, text: str) -> List[float]:
        """Generate embeddings using Ollama."""
        if ollama is None:
            raise ImportError("Ollama package not installed. Run: pip install ollama")

        response = ollama.embeddings(
            model=self.model,
            prompt=text
        )
        return response['embedding']


def get_ai_helper(
    provider: str = "openai",
    model: Optional[str] = None,
    fallback_to_ollama: bool = True
) -> AIHelper:
    """
    Get an AI helper instance with optional fallback.

    Args:
        provider: "openai" or "ollama"
        model: Model name (optional)
        fallback_to_ollama: If True, fallback to Ollama if OpenAI fails

    Returns:
        AIHelper instance
    """
    provider_enum = ModelProvider(provider.lower())

    try:
        return AIHelper(provider=provider_enum, model=model)
    except (ValueError, ImportError) as e:
        if fallback_to_ollama and provider_enum == ModelProvider.OPENAI:
            print(f"⚠️  OpenAI unavailable ({e}). Falling back to Ollama...")
            return AIHelper(provider=ModelProvider.OLLAMA, model=model or "llama3")
        raise


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)."""
    return len(text) // 4


def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    """Chunk text into smaller pieces for processing."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        word_size = estimate_tokens(word)
        if current_size + word_size > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
