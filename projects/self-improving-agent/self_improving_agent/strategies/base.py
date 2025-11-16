"""
Base strategy class.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Base class for response strategies.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize the strategy.

        Args:
            name: Strategy name
            config: Configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.performance_score = 0.0
        self.sample_count = 0

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """
        Get strategy parameters.

        Returns:
            Parameters dictionary
        """
        pass

    def update_performance(self, rating: float):
        """
        Update performance metrics.

        Args:
            rating: Rating received
        """
        self.sample_count += 1
        # Simple moving average
        self.performance_score = (
            (self.performance_score * (self.sample_count - 1) + rating) /
            self.sample_count
        )


class DetailedStrategy(BaseStrategy):
    """Strategy for detailed, comprehensive responses."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("detailed", config)

    def get_params(self) -> Dict[str, Any]:
        return {
            "style": "detailed",
            "include_examples": True,
            "include_next_steps": True
        }


class ConciseStrategy(BaseStrategy):
    """Strategy for brief, concise responses."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("concise", config)

    def get_params(self) -> Dict[str, Any]:
        return {
            "style": "concise",
            "max_length": "brief",
            "focus": "direct_answer"
        }


class StructuredStrategy(BaseStrategy):
    """Strategy for structured, organized responses."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("structured", config)

    def get_params(self) -> Dict[str, Any]:
        return {
            "style": "structured",
            "use_headings": True,
            "use_lists": True
        }
