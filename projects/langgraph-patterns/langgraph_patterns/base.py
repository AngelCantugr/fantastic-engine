"""
Base Pattern Class

All patterns inherit from this base class to ensure consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PatternConfig(BaseModel):
    """Base configuration for all patterns."""

    model: str = Field(default="gpt-4", description="LLM model to use")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens for response")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    streaming: bool = Field(default=False, description="Enable streaming responses")


class PatternResult(BaseModel):
    """Standard result format for all patterns."""

    output: str = Field(description="The final output from the agent")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Execution steps taken")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    success: bool = Field(default=True, description="Whether execution succeeded")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class BasePattern(ABC):
    """
    Base class for all LangGraph patterns.

    All patterns must implement:
    - build_graph(): Construct the LangGraph StateGraph
    - run(): Execute the pattern with given input
    """

    def __init__(self, config: Optional[PatternConfig] = None):
        """
        Initialize the pattern.

        Args:
            config: Pattern configuration
        """
        self.config = config or PatternConfig()
        self.graph = None
        self._setup()

    def _setup(self):
        """Setup the pattern (called during initialization)."""
        self.graph = self.build_graph()

    @abstractmethod
    def build_graph(self):
        """
        Build the LangGraph StateGraph for this pattern.

        Returns:
            StateGraph instance
        """
        pass

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> PatternResult:
        """
        Execute the pattern with given input.

        Args:
            input_text: The input query or task
            **kwargs: Additional pattern-specific arguments

        Returns:
            PatternResult with output and metadata
        """
        pass

    def visualize(self, output_path: Optional[str] = None) -> str:
        """
        Generate a visualization of the graph.

        Args:
            output_path: Optional path to save visualization

        Returns:
            Mermaid diagram as string
        """
        # TODO: Implement graph visualization
        return "# Graph visualization coming soon"

    def get_state(self) -> Dict[str, Any]:
        """
        Get current state of the pattern.

        Returns:
            Current state dictionary
        """
        # TODO: Implement state retrieval
        return {}
