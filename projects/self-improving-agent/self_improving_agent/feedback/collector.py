"""
Feedback collection module.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
import structlog

logger = structlog.get_logger()


class FeedbackRating(IntEnum):
    """Feedback rating enum."""
    TERRIBLE = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


@dataclass
class Feedback:
    """Feedback data structure."""
    response_id: str
    rating: FeedbackRating
    comment: Optional[str] = None
    prompt_version: Optional[str] = None
    strategy: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    implicit_signals: Dict[str, Any] = field(default_factory=dict)


class FeedbackCollector:
    """
    Collects and stores user feedback.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the feedback collector.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.feedbacks: List[Feedback] = []
        self.feedback_count = 0

    def collect(
        self,
        response_id: str,
        rating: int,
        comment: str = None,
        prompt_version: str = None,
        strategy: str = None,
        implicit_signals: Dict[str, Any] = None
    ) -> Feedback:
        """
        Collect feedback on a response.

        Args:
            response_id: Response ID
            rating: Rating (1-5)
            comment: Optional comment
            prompt_version: Prompt version used
            strategy: Strategy used
            implicit_signals: Optional implicit signals

        Returns:
            Feedback object
        """
        feedback = Feedback(
            response_id=response_id,
            rating=FeedbackRating(rating),
            comment=comment,
            prompt_version=prompt_version,
            strategy=strategy,
            implicit_signals=implicit_signals or {}
        )

        self.feedbacks.append(feedback)
        self.feedback_count += 1

        logger.info(
            "feedback_collected",
            response_id=response_id,
            rating=rating,
            total_feedbacks=self.feedback_count
        )

        return feedback

    def get_feedback_count(self) -> int:
        """Get total feedback count."""
        return self.feedback_count

    def get_feedbacks_by_rating(
        self,
        min_rating: int = None,
        max_rating: int = None
    ) -> List[Feedback]:
        """
        Get feedbacks filtered by rating range.

        Args:
            min_rating: Minimum rating
            max_rating: Maximum rating

        Returns:
            List of feedbacks
        """
        feedbacks = self.feedbacks

        if min_rating:
            feedbacks = [f for f in feedbacks if f.rating >= min_rating]

        if max_rating:
            feedbacks = [f for f in feedbacks if f.rating <= max_rating]

        return feedbacks

    def get_responses_by_rating(
        self,
        min_rating: int = None,
        max_rating: int = None
    ) -> List[str]:
        """
        Get response IDs filtered by rating.

        Args:
            min_rating: Minimum rating
            max_rating: Maximum rating

        Returns:
            List of response IDs
        """
        feedbacks = self.get_feedbacks_by_rating(min_rating, max_rating)
        return [f.response_id for f in feedbacks]

    def get_average_rating(self) -> float:
        """
        Get average rating.

        Returns:
            Average rating
        """
        if not self.feedbacks:
            return 0.0

        return sum(f.rating for f in self.feedbacks) / len(self.feedbacks)

    def get_rating_distribution(self) -> Dict[int, int]:
        """
        Get rating distribution.

        Returns:
            Dictionary of rating -> count
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for feedback in self.feedbacks:
            distribution[int(feedback.rating)] += 1

        return distribution
