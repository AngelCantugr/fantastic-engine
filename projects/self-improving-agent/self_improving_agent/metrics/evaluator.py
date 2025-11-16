"""
Performance evaluation module.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class PerformanceEvaluator:
    """
    Evaluates agent performance and improvement.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the performance evaluator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.baseline_metrics: Dict[str, float] = {}
        self.has_baseline = False

    def set_baseline(self, metrics: Dict[str, Any]):
        """
        Set baseline metrics for comparison.

        Args:
            metrics: Baseline metrics
        """
        self.baseline_metrics = {
            "average_rating": metrics.get("average_rating", 0.0),
            "success_rate": metrics.get("success_rate", 0.0),
            "avg_response_time": metrics.get("avg_response_time", 0.0),
            "cost_per_request": metrics.get("cost_per_request", 0.0)
        }
        self.has_baseline = True

        logger.info("baseline_set", baseline=self.baseline_metrics)

    def evaluate(self, current_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate current performance.

        Args:
            current_metrics: Current metrics (optional)

        Returns:
            Evaluation results
        """
        if current_metrics is None:
            # Would fetch from metrics tracker in production
            current_metrics = {
                "average_rating": 0.0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "cost_per_request": 0.0
            }

        evaluation = {
            **current_metrics
        }

        # Calculate improvement if baseline exists
        if self.has_baseline:
            rating_improvement = (
                (current_metrics["average_rating"] - self.baseline_metrics["average_rating"]) /
                self.baseline_metrics["average_rating"] * 100
                if self.baseline_metrics["average_rating"] > 0 else 0.0
            )

            evaluation["improvement_pct"] = rating_improvement
            evaluation["vs_baseline"] = {
                "rating": rating_improvement,
                "better": rating_improvement > 0
            }

        logger.info("performance_evaluated", metrics=evaluation)

        return evaluation
