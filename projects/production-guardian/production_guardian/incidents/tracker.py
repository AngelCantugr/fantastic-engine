"""
Incident tracking and management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import structlog

logger = structlog.get_logger()


class IncidentStatus(str, Enum):
    """Incident status enum."""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    AWAITING_APPROVAL = "awaiting_approval"
    REMEDIATED = "remediated"
    FAILED = "failed"
    MANUAL_INTERVENTION_REQUIRED = "manual_intervention_required"
    RESOLVED = "resolved"


@dataclass
class Incident:
    """Incident data class."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    severity: str = "low"
    source: str = "unknown"
    status: IncidentStatus = IncidentStatus.DETECTED
    details: Dict[str, Any] = field(default_factory=dict)
    remediation_result: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None


class IncidentTracker:
    """
    Tracks and manages incidents.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the incident tracker.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.incidents: Dict[str, Incident] = {}
        self.incident_count = 0

    def create_incident(
        self,
        description: str,
        severity: str,
        source: str,
        details: Dict[str, Any] = None
    ) -> Incident:
        """
        Create a new incident.

        Args:
            description: Incident description
            severity: Severity level
            source: Source of incident
            details: Additional details

        Returns:
            Created incident
        """
        incident = Incident(
            description=description,
            severity=severity,
            source=source,
            details=details or {}
        )

        self.incidents[incident.id] = incident
        self.incident_count += 1

        logger.info(
            "incident_created",
            incident_id=incident.id,
            severity=severity,
            source=source
        )

        return incident

    def update_incident(
        self,
        incident_id: str,
        status: str = None,
        remediation_result: Dict[str, Any] = None,
        reason: str = None,
        error: str = None
    ):
        """
        Update an incident.

        Args:
            incident_id: Incident ID
            status: New status
            remediation_result: Remediation result
            reason: Reason for update
            error: Error message
        """
        if incident_id not in self.incidents:
            logger.warning("incident_not_found", incident_id=incident_id)
            return

        incident = self.incidents[incident_id]

        if status:
            incident.status = IncidentStatus(status)

        if remediation_result:
            incident.remediation_result = remediation_result

        if error:
            if not incident.details:
                incident.details = {}
            incident.details["error"] = error

        if reason:
            if not incident.details:
                incident.details = {}
            incident.details["reason"] = reason

        incident.updated_at = datetime.utcnow().isoformat()

        if status in ["resolved", "remediated"]:
            incident.resolved_at = datetime.utcnow().isoformat()

        logger.info(
            "incident_updated",
            incident_id=incident_id,
            status=incident.status
        )

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """
        Get an incident by ID.

        Args:
            incident_id: Incident ID

        Returns:
            Incident or None
        """
        return self.incidents.get(incident_id)

    def get_active_incidents(self) -> List[Incident]:
        """
        Get all active incidents.

        Returns:
            List of active incidents
        """
        active_statuses = [
            IncidentStatus.DETECTED,
            IncidentStatus.ANALYZING,
            IncidentStatus.AWAITING_APPROVAL
        ]

        return [
            incident for incident in self.incidents.values()
            if incident.status in active_statuses
        ]

    def get_total_incidents(self) -> int:
        """Get total incident count."""
        return self.incident_count

    def get_incidents_by_severity(self, severity: str) -> List[Incident]:
        """
        Get incidents by severity.

        Args:
            severity: Severity level

        Returns:
            List of incidents
        """
        return [
            incident for incident in self.incidents.values()
            if incident.severity == severity
        ]
