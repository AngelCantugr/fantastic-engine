"""
Metrics collection and monitoring for SDLC workflows.
"""

from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()


@dataclass
class WorkflowEvent:
    """Workflow event for monitoring."""
    timestamp: str
    agent: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and tracks metrics for agent operations.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: Dict[str, Any] = {
            "workflows_started": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "total_duration": 0.0,
            "agent_calls": {},
            "costs": 0.0
        }

    def record_workflow_start(self, workflow_id: str):
        """Record workflow start."""
        self.metrics["workflows_started"] += 1
        logger.info("workflow_started", workflow_id=workflow_id)

    def record_workflow_complete(self, workflow_id: str, duration: float):
        """Record workflow completion."""
        self.metrics["workflows_completed"] += 1
        self.metrics["total_duration"] += duration
        logger.info(
            "workflow_completed",
            workflow_id=workflow_id,
            duration=duration
        )

    def record_workflow_failed(self, workflow_id: str, error: str):
        """Record workflow failure."""
        self.metrics["workflows_failed"] += 1
        logger.error("workflow_failed", workflow_id=workflow_id, error=error)

    def record_agent_call(self, agent: str, cost: float = 0.0):
        """Record agent call."""
        if agent not in self.metrics["agent_calls"]:
            self.metrics["agent_calls"][agent] = 0
        self.metrics["agent_calls"][agent] += 1
        self.metrics["costs"] += cost

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            **self.metrics,
            "average_duration": (
                self.metrics["total_duration"] / self.metrics["workflows_completed"]
                if self.metrics["workflows_completed"] > 0 else 0.0
            )
        }

    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            "workflows_started": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "total_duration": 0.0,
            "agent_calls": {},
            "costs": 0.0
        }


class WorkflowMonitor:
    """
    Monitors workflow execution and collects events.
    """

    def __init__(self):
        """Initialize the workflow monitor."""
        self.events: List[WorkflowEvent] = []
        self.metrics = MetricsCollector()

    def log_event(self, event: WorkflowEvent):
        """
        Log a workflow event.

        Args:
            event: Workflow event
        """
        self.events.append(event)
        logger.debug(
            "event_logged",
            agent=event.agent,
            message=event.message
        )

    def get_events(
        self,
        agent: str = None,
        limit: int = None
    ) -> List[WorkflowEvent]:
        """
        Get workflow events.

        Args:
            agent: Optional agent filter
            limit: Optional limit on number of events

        Returns:
            List of events
        """
        events = self.events

        if agent:
            events = [e for e in events if e.agent == agent]

        if limit:
            events = events[-limit:]

        return events

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics."""
        return self.metrics.get_metrics()

    def clear(self):
        """Clear all events and metrics."""
        self.events.clear()
        self.metrics.reset()
