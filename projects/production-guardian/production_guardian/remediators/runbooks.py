"""
Runbook execution engine.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import yaml
import structlog

logger = structlog.get_logger()


@dataclass
class Runbook:
    """
    Runbook definition.
    """
    name: str
    trigger: Dict[str, Any]
    steps: List[Dict[str, Any]]
    metadata: Dict[str, Any] = None

    @classmethod
    def from_yaml(cls, yaml_file: str) -> "Runbook":
        """
        Load runbook from YAML file.

        Args:
            yaml_file: Path to YAML file

        Returns:
            Runbook instance
        """
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            name=data["name"],
            trigger=data["trigger"],
            steps=data["steps"],
            metadata=data.get("metadata", {})
        )


class RunbookExecutor:
    """
    Executes runbooks for automated remediation.
    """

    def __init__(self, config: Dict[str, Any] = None, dry_run: bool = True):
        """
        Initialize the runbook executor.

        Args:
            config: Configuration dictionary
            dry_run: Whether to run in dry-run mode
        """
        self.config = config or {}
        self.dry_run = dry_run
        self.runbooks: List[Runbook] = []
        self.execution_count = 0

    def add_runbook(self, runbook: Runbook):
        """
        Add a runbook.

        Args:
            runbook: Runbook to add
        """
        self.runbooks.append(runbook)
        logger.info("runbook_added", name=runbook.name)

    def find_runbook(self, anomaly: Dict[str, Any]) -> Optional[Runbook]:
        """
        Find a matching runbook for an anomaly.

        Args:
            anomaly: Anomaly details

        Returns:
            Matching runbook or None
        """
        for runbook in self.runbooks:
            if self._matches_trigger(runbook.trigger, anomaly):
                return runbook
        return None

    def _matches_trigger(self, trigger: Dict[str, Any], anomaly: Dict[str, Any]) -> bool:
        """
        Check if trigger matches anomaly.

        Args:
            trigger: Runbook trigger
            anomaly: Anomaly details

        Returns:
            Whether trigger matches
        """
        # Simple matching on type
        if "type" in trigger and trigger["type"] == anomaly.get("type"):
            return True

        # Metric-based matching
        if "metric" in trigger:
            return trigger["metric"] in anomaly.get("type", "")

        return False

    async def execute(self, runbook: Runbook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a runbook.

        Args:
            runbook: Runbook to execute
            context: Execution context

        Returns:
            Execution result
        """
        logger.info(
            "runbook_execution_started",
            name=runbook.name,
            dry_run=self.dry_run
        )

        self.execution_count += 1
        results = []

        try:
            for step in runbook.steps:
                step_name = step.get("name", "unnamed_step")
                action = step.get("action")

                logger.info("executing_step", step=step_name, action=action)

                # Execute step (simplified - in production would dispatch to actual remediators)
                if self.dry_run:
                    result = {
                        "success": True,
                        "message": f"[DRY RUN] Executed {action}"
                    }
                else:
                    # In production, would execute actual remediation
                    result = {"success": True, "message": f"Executed {action}"}

                results.append({
                    "step": step_name,
                    "action": action,
                    "result": result
                })

            logger.info(
                "runbook_execution_complete",
                name=runbook.name,
                steps_executed=len(results)
            )

            return {
                "success": True,
                "runbook": runbook.name,
                "steps_executed": len(results),
                "results": results
            }

        except Exception as e:
            logger.error(
                "runbook_execution_failed",
                name=runbook.name,
                error=str(e)
            )
            return {
                "success": False,
                "runbook": runbook.name,
                "error": str(e),
                "results": results
            }
