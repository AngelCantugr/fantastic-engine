"""
Metrics tracking module.
"""

from typing import Dict, Any, List
from collections import defaultdict, deque
from datetime import datetime
import structlog

logger = structlog.get_logger()


class MetricsTracker:
    """
    Tracks performance metrics for the agent.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the metrics tracker.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.metrics_window = self.config.get("metrics_window", 7)  # days

        # Metrics storage
        self.requests = []
        self.feedbacks = {}
        self.ratings = deque(maxlen=1000)
        self.costs = []
        self.response_times = deque(maxlen=1000)

        # Aggregated metrics
        self.total_requests = 0
        self.total_feedbacks = 0
        self.total_cost = 0.0

    def record_request(
        self,
        request_id: str,
        prompt_version: str,
        strategy: str,
        response_time: float
    ):
        """
        Record a request.

        Args:
            request_id: Request ID
            prompt_version: Prompt version used
            strategy: Strategy used
            response_time: Response time in seconds
        """
        self.requests.append({
            "id": request_id,
            "prompt_version": prompt_version,
            "strategy": strategy,
            "response_time": response_time,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.total_requests += 1
        self.response_times.append(response_time)

        logger.debug("request_recorded", request_id=request_id)

    def record_feedback(self, response_id: str, rating: int):
        """
        Record feedback.

        Args:
            response_id: Response ID
            rating: Rating (1-5)
        """
        self.feedbacks[response_id] = rating
        self.ratings.append(rating)
        self.total_feedbacks += 1

        logger.debug("feedback_recorded", response_id=response_id, rating=rating)

    def record_cost(self, cost: float):
        """
        Record API cost.

        Args:
            cost: Cost in USD
        """
        self.costs.append(cost)
        self.total_cost += cost

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Get summary metrics.

        Returns:
            Metrics dictionary
        """
        avg_rating = sum(self.ratings) / len(self.ratings) if self.ratings else 0.0
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0.0
        )

        success_rate = (
            sum(1 for r in self.ratings if r >= 4) / len(self.ratings) * 100
            if self.ratings else 0.0
        )

        return {
            "total_requests": self.total_requests,
            "total_feedbacks": self.total_feedbacks,
            "average_rating": avg_rating,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_cost": self.total_cost,
            "cost_per_request": (
                self.total_cost / self.total_requests
                if self.total_requests > 0 else 0.0
            )
        }
