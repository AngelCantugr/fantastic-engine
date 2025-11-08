"""
LLM Client for AI-powered data validation and analysis.

Supports multiple LLM providers: Anthropic (Claude), OpenAI (GPT-4), and local models.
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
import anthropic
import openai
from loguru import logger


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL = "local"  # For future Ollama support


class LLMClient:
    """
    Unified client for interacting with different LLM providers.

    Examples:
        >>> client = LLMClient(provider="anthropic")
        >>> response = client.generate("Explain this data anomaly: ...")
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ("anthropic", "openai", "local")
            model: Model name (defaults based on provider)
            api_key: API key (reads from env if not provided)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        self.provider = LLMProvider(provider)
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set default models if not specified
        if model is None:
            if self.provider == LLMProvider.ANTHROPIC:
                self.model = "claude-3-5-sonnet-20241022"
            elif self.provider == LLMProvider.OPENAI:
                self.model = "gpt-4-turbo-preview"
            else:
                self.model = "llama2"  # Default local model
        else:
            self.model = model

        # Initialize provider client
        if self.provider == LLMProvider.ANTHROPIC:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif self.provider == LLMProvider.OPENAI:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            openai.api_key = api_key
            self.client = openai

        logger.info(f"Initialized {self.provider} client with model {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                return self._generate_anthropic(prompt, system_prompt, **kwargs)
            elif self.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt, system_prompt, **kwargs)
            else:
                raise NotImplementedError(f"Provider {self.provider} not implemented")

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate using Anthropic Claude API."""
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            system=system_prompt or "You are a data quality expert.",
            messages=messages
        )

        return response.content[0].text

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate using OpenAI GPT API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )

        return response.choices[0].message.content

    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output matching a schema.

        Useful for extracting specific fields from analysis.

        Args:
            prompt: User prompt
            schema: JSON schema for expected output
            system_prompt: System prompt

        Returns:
            Parsed structured response
        """
        # Add schema to prompt
        schema_prompt = f"""
{prompt}

Respond with valid JSON matching this schema:
{schema}
"""
        response = self.generate(schema_prompt, system_prompt)

        # Parse JSON from response
        import json
        import re

        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning raw text")
            return {"raw_response": response}

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[str]:
        """
        Generate responses for multiple prompts (with rate limiting).

        Args:
            prompts: List of prompts
            system_prompt: System prompt for all requests
            max_concurrent: Maximum concurrent requests

        Returns:
            List of generated responses
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def generate_single(prompt):
            return self.generate(prompt, system_prompt)

        # Use thread pool to handle rate limiting
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            responses = list(executor.map(generate_single, prompts))

        return responses

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Estimate cost for API call.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Pricing as of Jan 2025 (update as needed)
        pricing = {
            "claude-3-5-sonnet-20241022": {
                "input": 0.003 / 1000,   # $3 per MTok
                "output": 0.015 / 1000   # $15 per MTok
            },
            "gpt-4-turbo-preview": {
                "input": 0.01 / 1000,
                "output": 0.03 / 1000
            }
        }

        if self.model in pricing:
            prices = pricing[self.model]
            cost = (prompt_tokens * prices["input"]) + \
                   (completion_tokens * prices["output"])
            return cost
        else:
            return 0.0  # Unknown model or local

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Approximate token count
        """
        # Rough approximation: ~4 chars per token
        return len(text) // 4


# Convenience functions
def get_client(provider: str = "anthropic", **kwargs) -> LLMClient:
    """Get LLM client instance."""
    return LLMClient(provider=provider, **kwargs)


def quick_generate(prompt: str, provider: str = "anthropic") -> str:
    """Quick one-off generation."""
    client = get_client(provider)
    return client.generate(prompt)
