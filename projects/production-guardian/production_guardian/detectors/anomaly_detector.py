"""
Anomaly detection using statistical and ML methods.
"""

from typing import Dict, Any, List
from collections import defaultdict, deque
from datetime import datetime
import numpy as np
import structlog

logger = structlog.get_logger()


class AnomalyDetector:
    """
    Detects anomalies in logs and metrics using statistical methods.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the anomaly detector.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_rate_threshold = self.config.get("error_rate_threshold", 5.0)
        self.cpu_threshold = self.config.get("cpu_threshold", 80)
        self.memory_threshold = self.config.get("memory_threshold", 90)

        # Historical data for statistical analysis
        self.log_history = deque(maxlen=1000)
        self.metrics_history = deque(maxlen=100)

        self.anomaly_count = 0

    def detect_log_anomalies(self, log_batch: List[str]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in log batch.

        Args:
            log_batch: Batch of log lines

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Count error patterns
        error_count = sum(1 for log in log_batch if self._is_error_log(log))
        error_rate = (error_count / len(log_batch) * 100) if log_batch else 0

        if error_rate > self.error_rate_threshold:
            self.anomaly_count += 1
            anomalies.append({
                "type": "high_error_rate",
                "severity": self._calculate_severity(error_rate, self.error_rate_threshold),
                "description": f"High error rate: {error_rate:.2f}%",
                "value": error_rate,
                "threshold": self.error_rate_threshold,
                "proposed_action": "restart_service",
                "timestamp": datetime.utcnow().isoformat()
            })

        # Store in history
        self.log_history.extend(log_batch)

        return anomalies

    def detect_metric_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics.

        Args:
            metrics: Metrics dictionary

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check system metrics
        if "system" in metrics:
            system = metrics["system"]

            # CPU anomaly
            if system.get("cpu_percent", 0) > self.cpu_threshold:
                self.anomaly_count += 1
                anomalies.append({
                    "type": "high_cpu",
                    "severity": self._calculate_severity(
                        system["cpu_percent"],
                        self.cpu_threshold
                    ),
                    "description": f"High CPU usage: {system['cpu_percent']:.1f}%",
                    "value": system["cpu_percent"],
                    "threshold": self.cpu_threshold,
                    "proposed_action": "identify_cpu_processes",
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Memory anomaly
            if system.get("memory_percent", 0) > self.memory_threshold:
                self.anomaly_count += 1
                anomalies.append({
                    "type": "high_memory",
                    "severity": self._calculate_severity(
                        system["memory_percent"],
                        self.memory_threshold
                    ),
                    "description": f"High memory usage: {system['memory_percent']:.1f}%",
                    "value": system["memory_percent"],
                    "threshold": self.memory_threshold,
                    "proposed_action": "restart_service",
                    "timestamp": datetime.utcnow().isoformat()
                })

        # Store in history
        self.metrics_history.append(metrics)

        return anomalies

    def _is_error_log(self, log: str) -> bool:
        """Check if log is an error."""
        error_keywords = ["ERROR", "FATAL", "CRITICAL", "Exception", "Traceback"]
        return any(keyword in log for keyword in error_keywords)

    def _calculate_severity(self, value: float, threshold: float) -> str:
        """
        Calculate severity based on how much value exceeds threshold.

        Args:
            value: Current value
            threshold: Threshold value

        Returns:
            Severity level
        """
        if value < threshold:
            return "low"

        excess = (value - threshold) / threshold * 100

        if excess < 10:
            return "medium"
        elif excess < 30:
            return "high"
        else:
            return "critical"

    def get_anomaly_count(self) -> int:
        """Get total anomalies detected."""
        return self.anomaly_count
