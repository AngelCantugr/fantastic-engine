"""
Base agent class for SDLC agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import structlog

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for all SDLC agents.

    Provides common functionality for agent initialization, configuration,
    and interaction with LLMs.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the base agent.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.model_name = self.config.get("model_name", "gpt-4-turbo-preview")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Metrics
        self.total_calls = 0
        self.total_cost = 0.0
        self.total_tokens = 0

        logger.info(
            "agent_initialized",
            agent_type=self.__class__.__name__,
            model=self.model_name
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_user_prompt_template(self) -> str:
        """
        Get the user prompt template for this agent.

        Returns:
            User prompt template string
        """
        pass

    def create_prompt(self, **kwargs) -> ChatPromptTemplate:
        """
        Create a chat prompt from system and user templates.

        Args:
            **kwargs: Variables for the user prompt template

        Returns:
            ChatPromptTemplate
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("user", self.get_user_prompt_template())
        ])

    def invoke_llm(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        """
        Invoke the LLM with a prompt.

        Args:
            prompt: Chat prompt template
            **kwargs: Variables for the prompt

        Returns:
            LLM response content
        """
        self.total_calls += 1

        try:
            # Create chain
            chain = prompt | self.llm

            # Invoke
            response = chain.invoke(kwargs)

            # Track metrics (simplified - actual cost calculation would need token counting)
            self.total_tokens += len(response.content)

            logger.debug(
                "llm_invoked",
                agent_type=self.__class__.__name__,
                total_calls=self.total_calls
            )

            return response.content

        except Exception as e:
            logger.error(
                "llm_invocation_failed",
                agent_type=self.__class__.__name__,
                error=str(e)
            )
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics.

        Returns:
            Metrics dictionary
        """
        return {
            "agent_type": self.__class__.__name__,
            "total_calls": self.total_calls,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens
        }

    def reset_metrics(self):
        """Reset agent metrics."""
        self.total_calls = 0
        self.total_cost = 0.0
        self.total_tokens = 0
