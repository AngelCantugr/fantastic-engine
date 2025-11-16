"""
Shared state management for multi-agent SDLC orchestration.
"""

from typing import TypedDict, Annotated, Optional
from datetime import datetime
from enum import Enum


class DeploymentStatus(str, Enum):
    """Deployment status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ReviewSeverity(str, Enum):
    """Code review severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReviewResult(TypedDict):
    """Code review result structure"""
    approved: bool
    severity: ReviewSeverity
    issues: list[dict]
    comments: list[str]
    timestamp: str


class TestResult(TypedDict):
    """Test generation result structure"""
    tests_generated: list[str]
    coverage_estimate: float
    framework: str
    runnable: bool
    timestamp: str


class DeploymentResult(TypedDict):
    """Deployment result structure"""
    status: DeploymentStatus
    target_environment: str
    artifacts: list[str]
    health_check_passed: bool
    rollback_available: bool
    timestamp: str


class AgentMessage(TypedDict):
    """Message structure for inter-agent communication"""
    agent: str
    action: str
    data: dict
    timestamp: str
    correlation_id: str


class SDLCState(TypedDict):
    """
    Shared state for SDLC orchestration.

    This state is passed between agents and maintained by LangGraph.
    """
    # Input
    code_changes: str
    target_branch: str
    deployment_target: str

    # Agent Results
    review_result: Optional[ReviewResult]
    test_result: Optional[TestResult]
    deployment_result: Optional[DeploymentResult]

    # Communication
    messages: Annotated[list[AgentMessage], "Message history between agents"]

    # Workflow Control
    current_step: str
    errors: list[str]
    warnings: list[str]

    # Metadata
    workflow_id: str
    started_at: str
    completed_at: Optional[str]
    total_cost: float

    # Safety
    dry_run: bool
    approval_required: bool
    approved_by: Optional[str]


def create_initial_state(
    code_changes: str,
    target_branch: str = "main",
    deployment_target: str = "staging",
    dry_run: bool = True
) -> SDLCState:
    """
    Create an initial state for SDLC orchestration.

    Args:
        code_changes: Path to code changes or diff content
        target_branch: Git branch to target
        deployment_target: Deployment environment (staging/production)
        dry_run: Whether to run in dry-run mode

    Returns:
        Initial SDLCState
    """
    import uuid

    return SDLCState(
        code_changes=code_changes,
        target_branch=target_branch,
        deployment_target=deployment_target,
        review_result=None,
        test_result=None,
        deployment_result=None,
        messages=[],
        current_step="code_review",
        errors=[],
        warnings=[],
        workflow_id=str(uuid.uuid4()),
        started_at=datetime.utcnow().isoformat(),
        completed_at=None,
        total_cost=0.0,
        dry_run=dry_run,
        approval_required=deployment_target == "production",
        approved_by=None
    )


def add_message(state: SDLCState, agent: str, action: str, data: dict) -> SDLCState:
    """
    Add a message to the state.

    Args:
        state: Current state
        agent: Agent name
        action: Action performed
        data: Action data

    Returns:
        Updated state
    """
    import uuid

    message = AgentMessage(
        agent=agent,
        action=action,
        data=data,
        timestamp=datetime.utcnow().isoformat(),
        correlation_id=state["workflow_id"]
    )

    return {
        **state,
        "messages": state["messages"] + [message]
    }
