"""
Main Guardian Agent implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import asyncio

from production_guardian.monitors.log_monitor import LogMonitor
from production_guardian.monitors.metrics_monitor import MetricsMonitor
from production_guardian.detectors.anomaly_detector import AnomalyDetector
from production_guardian.remediators.runbooks import RunbookExecutor, Runbook
from production_guardian.safety.gates import SafetyGate
from production_guardian.safety.limits import ActionLimiter
from production_guardian.incidents.tracker import IncidentTracker

logger = structlog.get_logger()


class GuardianAgent:
    """
    Production Guardian Agent - Monitors and remediates production issues.

    This agent continuously monitors production systems through logs and metrics,
    detects anomalies, and performs automated remediation with safety guardrails.
    """

    def __init__(
        self,
        config: Dict[str, Any] = None,
        runbooks: List[Runbook] = None,
        dry_run: bool = True
    ):
        """
        Initialize the Guardian Agent.

        Args:
            config: Configuration dictionary
            runbooks: List of runbooks to use
            dry_run: Whether to run in dry-run mode (no actual actions)
        """
        self.config = config or {}
        self.dry_run = dry_run

        # Initialize components
        self.log_monitor = LogMonitor(config)
        self.metrics_monitor = MetricsMonitor(config)
        self.anomaly_detector = AnomalyDetector(config)
        self.runbook_executor = RunbookExecutor(config, dry_run=dry_run)
        self.safety_gate = SafetyGate(config)
        self.action_limiter = ActionLimiter(config)
        self.incident_tracker = IncidentTracker(config)

        # Load runbooks
        if runbooks:
            for runbook in runbooks:
                self.runbook_executor.add_runbook(runbook)

        # State
        self.is_running = False
        self.monitoring_task = None

        logger.info(
            "guardian_agent_initialized",
            dry_run=dry_run,
            runbook_count=len(runbooks) if runbooks else 0
        )

    async def start_monitoring(
        self,
        log_file: Optional[str] = None,
        metrics_endpoint: Optional[str] = None
    ):
        """
        Start continuous monitoring of production systems.

        Args:
            log_file: Path to log file to monitor
            metrics_endpoint: Metrics endpoint URL (e.g., Prometheus)
        """
        logger.info("starting_guardian_monitoring", dry_run=self.dry_run)

        self.is_running = True

        # Start monitoring tasks
        tasks = []

        if log_file or self.config.get("log_file_path"):
            log_path = log_file or self.config["log_file_path"]
            tasks.append(self._monitor_logs(log_path))

        if metrics_endpoint or self.config.get("metrics_endpoint"):
            endpoint = metrics_endpoint or self.config["metrics_endpoint"]
            tasks.append(self._monitor_metrics(endpoint))

        # Run monitoring tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error("monitoring_error", error=str(e))
            raise

    async def _monitor_logs(self, log_file: str):
        """
        Monitor logs continuously.

        Args:
            log_file: Path to log file
        """
        logger.info("log_monitoring_started", log_file=log_file)

        async for log_batch in self.log_monitor.stream_logs(log_file):
            # Detect anomalies in logs
            anomalies = self.anomaly_detector.detect_log_anomalies(log_batch)

            if anomalies:
                await self._handle_anomalies(anomalies, source="logs")

    async def _monitor_metrics(self, endpoint: str):
        """
        Monitor metrics continuously.

        Args:
            endpoint: Metrics endpoint URL
        """
        logger.info("metrics_monitoring_started", endpoint=endpoint)

        async for metrics_batch in self.metrics_monitor.stream_metrics(endpoint):
            # Detect anomalies in metrics
            anomalies = self.anomaly_detector.detect_metric_anomalies(metrics_batch)

            if anomalies:
                await self._handle_anomalies(anomalies, source="metrics")

    async def _handle_anomalies(self, anomalies: List[Dict], source: str):
        """
        Handle detected anomalies.

        Args:
            anomalies: List of detected anomalies
            source: Source of anomalies (logs or metrics)
        """
        for anomaly in anomalies:
            logger.warning("anomaly_detected", anomaly=anomaly, source=source)

            # Create incident
            incident = self.incident_tracker.create_incident(
                description=anomaly["description"],
                severity=anomaly["severity"],
                source=source,
                details=anomaly
            )

            # Determine if remediation is needed
            if self._should_remediate(anomaly):
                # Check safety gates
                safe_to_proceed = self.safety_gate.check(
                    action_type=anomaly["proposed_action"],
                    severity=anomaly["severity"]
                )

                if safe_to_proceed:
                    # Check action limits
                    within_limits = self.action_limiter.check_limit(
                        action_type=anomaly["proposed_action"]
                    )

                    if within_limits:
                        # Execute remediation
                        await self._execute_remediation(incident, anomaly)
                    else:
                        logger.warning("action_limit_exceeded", incident_id=incident.id)
                        self.incident_tracker.update_incident(
                            incident.id,
                            status="awaiting_approval",
                            reason="Action limit exceeded"
                        )
                else:
                    logger.warning("safety_gate_blocked", incident_id=incident.id)
                    self.incident_tracker.update_incident(
                        incident.id,
                        status="awaiting_approval",
                        reason="Safety gate blocked"
                    )

    def _should_remediate(self, anomaly: Dict) -> bool:
        """
        Determine if anomaly should trigger remediation.

        Args:
            anomaly: Anomaly details

        Returns:
            Whether to remediate
        """
        severity = anomaly.get("severity", "low")
        return severity in ["medium", "high", "critical"]

    async def _execute_remediation(self, incident, anomaly: Dict):
        """
        Execute remediation for an anomaly.

        Args:
            incident: Incident object
            anomaly: Anomaly details
        """
        logger.info("executing_remediation", incident_id=incident.id, dry_run=self.dry_run)

        try:
            # Find matching runbook
            runbook = self.runbook_executor.find_runbook(anomaly)

            if runbook:
                # Execute runbook
                result = await self.runbook_executor.execute(runbook, anomaly)

                # Record action
                self.action_limiter.record_action(anomaly["proposed_action"])

                # Update incident
                self.incident_tracker.update_incident(
                    incident.id,
                    status="remediated" if result["success"] else "failed",
                    remediation_result=result
                )

                logger.info(
                    "remediation_complete",
                    incident_id=incident.id,
                    success=result["success"]
                )
            else:
                logger.warning("no_runbook_found", incident_id=incident.id)
                self.incident_tracker.update_incident(
                    incident.id,
                    status="manual_intervention_required",
                    reason="No matching runbook"
                )

        except Exception as e:
            logger.error("remediation_failed", incident_id=incident.id, error=str(e))
            self.incident_tracker.update_incident(
                incident.id,
                status="failed",
                error=str(e)
            )

    def stop_monitoring(self):
        """Stop monitoring."""
        logger.info("stopping_guardian_monitoring")
        self.is_running = False

    def get_active_incidents(self) -> List[Any]:
        """
        Get active incidents.

        Returns:
            List of active incidents
        """
        return self.incident_tracker.get_active_incidents()

    def approve_action(self, incident_id: str, approved: bool):
        """
        Approve or deny a pending action.

        Args:
            incident_id: Incident ID
            approved: Whether action is approved
        """
        logger.info("action_approval", incident_id=incident_id, approved=approved)

        if approved:
            # Execute the pending action
            incident = self.incident_tracker.get_incident(incident_id)
            # Implementation would execute the action here
            self.incident_tracker.update_incident(
                incident_id,
                status="approved_executing"
            )
        else:
            self.incident_tracker.update_incident(
                incident_id,
                status="denied"
            )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics.

        Returns:
            Metrics dictionary
        """
        return {
            "incidents_total": self.incident_tracker.get_total_incidents(),
            "incidents_active": len(self.get_active_incidents()),
            "actions_taken": self.action_limiter.get_action_count(),
            "anomalies_detected": self.anomaly_detector.get_anomaly_count(),
            "dry_run": self.dry_run
        }
