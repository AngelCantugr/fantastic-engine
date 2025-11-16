"""
Action limits and rate limiting for automated actions.
"""

from typing import Dict, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class ActionLimiter:
    """
    Limits the number of automated actions per time period.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the action limiter.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.max_actions_per_hour = self.config.get("max_actions_per_hour", 10)
        self.max_actions_per_day = self.config.get("max_actions_per_day", 50)
        self.cooldown_period = self.config.get("cooldown_period", 300)  # 5 minutes

        # Track actions
        self.action_history = deque()
        self.action_counts = defaultdict(int)
        self.last_action_time = {}

    def check_limit(self, action_type: str) -> bool:
        """
        Check if action is within limits.

        Args:
            action_type: Type of action

        Returns:
            True if within limits
        """
        now = datetime.utcnow()

        # Check cooldown period
        if action_type in self.last_action_time:
            last_time = self.last_action_time[action_type]
            if (now - last_time).total_seconds() < self.cooldown_period:
                logger.warning(
                    "action_in_cooldown",
                    action=action_type,
                    cooldown_remaining=(
                        self.cooldown_period - (now - last_time).total_seconds()
                    )
                )
                return False

        # Clean old actions from history
        self._clean_old_actions(now)

        # Count recent actions
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_hour = sum(1 for timestamp, _ in self.action_history if timestamp > hour_ago)
        recent_day = sum(1 for timestamp, _ in self.action_history if timestamp > day_ago)

        # Check limits
        if recent_hour >= self.max_actions_per_hour:
            logger.warning(
                "hourly_limit_exceeded",
                action=action_type,
                recent_hour=recent_hour,
                limit=self.max_actions_per_hour
            )
            return False

        if recent_day >= self.max_actions_per_day:
            logger.warning(
                "daily_limit_exceeded",
                action=action_type,
                recent_day=recent_day,
                limit=self.max_actions_per_day
            )
            return False

        logger.info(
            "action_limit_check_passed",
            action=action_type,
            recent_hour=recent_hour,
            recent_day=recent_day
        )
        return True

    def record_action(self, action_type: str):
        """
        Record an action.

        Args:
            action_type: Type of action
        """
        now = datetime.utcnow()
        self.action_history.append((now, action_type))
        self.action_counts[action_type] += 1
        self.last_action_time[action_type] = now

        logger.info(
            "action_recorded",
            action=action_type,
            total_count=self.action_counts[action_type]
        )

    def _clean_old_actions(self, now: datetime):
        """Remove actions older than 1 day from history."""
        day_ago = now - timedelta(days=1)
        while self.action_history and self.action_history[0][0] < day_ago:
            self.action_history.popleft()

    def get_action_count(self) -> int:
        """Get total action count."""
        return sum(self.action_counts.values())

    def get_action_stats(self) -> Dict[str, Any]:
        """
        Get action statistics.

        Returns:
            Statistics dictionary
        """
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        return {
            "total_actions": self.get_action_count(),
            "actions_last_hour": sum(
                1 for timestamp, _ in self.action_history if timestamp > hour_ago
            ),
            "actions_last_day": sum(
                1 for timestamp, _ in self.action_history if timestamp > day_ago
            ),
            "actions_by_type": dict(self.action_counts)
        }
