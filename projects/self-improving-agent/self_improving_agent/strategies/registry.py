"""
Strategy registry for managing multiple strategies.
"""

from typing import Dict, Any, List
from self_improving_agent.strategies.base import (
    BaseStrategy,
    DetailedStrategy,
    ConciseStrategy,
    StructuredStrategy
)
import structlog

logger = structlog.get_logger()


class StrategyRegistry:
    """
    Registry for managing response strategies.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the strategy registry.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.strategies: Dict[str, BaseStrategy] = {}
        self.active_strategy_name: str = "detailed"

        # Register default strategies
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register default strategies."""
        self.register_strategy(DetailedStrategy(self.config))
        self.register_strategy(ConciseStrategy(self.config))
        self.register_strategy(StructuredStrategy(self.config))

        logger.info("default_strategies_registered", count=len(self.strategies))

    def register_strategy(self, strategy: BaseStrategy):
        """
        Register a strategy.

        Args:
            strategy: Strategy to register
        """
        self.strategies[strategy.name] = strategy
        logger.info("strategy_registered", name=strategy.name)

    def get_active_strategy(self) -> BaseStrategy:
        """
        Get the active strategy.

        Returns:
            Active BaseStrategy
        """
        return self.strategies[self.active_strategy_name]

    def set_active_strategy(self, strategy_name: str):
        """
        Set the active strategy.

        Args:
            strategy_name: Name of strategy to activate
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")

        self.active_strategy_name = strategy_name
        logger.info("active_strategy_changed", strategy=strategy_name)

    def get_all_strategies(self) -> List[BaseStrategy]:
        """
        Get all registered strategies.

        Returns:
            List of strategies
        """
        return list(self.strategies.values())

    def get_best_strategy(self) -> BaseStrategy:
        """
        Get the best performing strategy.

        Returns:
            Best performing BaseStrategy
        """
        return max(
            self.strategies.values(),
            key=lambda s: s.performance_score
        )
