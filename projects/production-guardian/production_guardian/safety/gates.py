"""
Safety gates for controlling automated actions.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class SafetyGate:
    """
    Safety gate that controls which automated actions can proceed.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the safety gate.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.approval_threshold = self.config.get("require_approval_threshold", "medium")

        # Actions that always require approval
        self.always_require_approval = self.config.get(
            "require_approval_for",
            [
                "database_operations",
                "traffic_routing",
                "instance_termination"
            ]
        )

        self.severity_order = ["low", "medium", "high", "critical"]

    def check(self, action_type: str, severity: str) -> bool:
        """
        Check if an action can proceed without approval.

        Args:
            action_type: Type of action
            severity: Severity level

        Returns:
            True if action can proceed without approval
        """
        # Always block critical actions that require approval
        if action_type in self.always_require_approval:
            logger.info(
                "safety_gate_blocked",
                action=action_type,
                reason="requires_approval"
            )
            return False

        # Check severity threshold
        if self._severity_exceeds_threshold(severity):
            logger.info(
                "safety_gate_blocked",
                action=action_type,
                severity=severity,
                threshold=self.approval_threshold
            )
            return False

        logger.info("safety_gate_passed", action=action_type, severity=severity)
        return True

    def _severity_exceeds_threshold(self, severity: str) -> bool:
        """
        Check if severity exceeds approval threshold.

        Args:
            severity: Severity level

        Returns:
            True if severity exceeds threshold
        """
        try:
            severity_idx = self.severity_order.index(severity.lower())
            threshold_idx = self.severity_order.index(self.approval_threshold.lower())
            return severity_idx >= threshold_idx
        except ValueError:
            # Unknown severity, be conservative
            return True
