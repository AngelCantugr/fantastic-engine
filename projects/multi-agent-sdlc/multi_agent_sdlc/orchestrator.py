"""
LangGraph orchestration for multi-agent SDLC workflow.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from multi_agent_sdlc.state import SDLCState, create_initial_state, add_message
from multi_agent_sdlc.agents.code_review import CodeReviewAgent
from multi_agent_sdlc.agents.test_generator import TestGeneratorAgent
from multi_agent_sdlc.agents.deployment import DeploymentAgent
import structlog

logger = structlog.get_logger()


class SDLCOrchestrator:
    """
    Orchestrates the multi-agent SDLC workflow using LangGraph.

    The workflow:
    1. Code Review Agent analyzes changes
    2. If approved, Test Generator Agent creates tests
    3. If tests pass, Deployment Agent deploys
    4. Each step can fail and route accordingly
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the orchestrator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.code_review_agent = CodeReviewAgent(config)
        self.test_generator_agent = TestGeneratorAgent(config)
        self.deployment_agent = DeploymentAgent(config)

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            Compiled StateGraph
        """
        # Create state graph
        workflow = StateGraph(SDLCState)

        # Add nodes
        workflow.add_node("code_review", self._code_review_node)
        workflow.add_node("test_generation", self._test_generation_node)
        workflow.add_node("deployment", self._deployment_node)
        workflow.add_node("feedback", self._feedback_node)
        workflow.add_node("success", self._success_node)

        # Set entry point
        workflow.set_entry_point("code_review")

        # Add conditional edges
        workflow.add_conditional_edges(
            "code_review",
            self._route_after_review,
            {
                "test_generation": "test_generation",
                "feedback": "feedback"
            }
        )

        workflow.add_conditional_edges(
            "test_generation",
            self._route_after_testing,
            {
                "deployment": "deployment",
                "feedback": "feedback"
            }
        )

        workflow.add_conditional_edges(
            "deployment",
            self._route_after_deployment,
            {
                "success": "success",
                "feedback": "feedback"
            }
        )

        # Terminal nodes
        workflow.add_edge("feedback", END)
        workflow.add_edge("success", END)

        # Compile the graph
        return workflow.compile()

    def _code_review_node(self, state: SDLCState) -> SDLCState:
        """
        Code review agent node.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("code_review_started", workflow_id=state["workflow_id"])

        try:
            # Perform code review
            review_result = self.code_review_agent.review(state["code_changes"])

            # Update state
            state = {
                **state,
                "review_result": review_result,
                "current_step": "code_review_complete"
            }

            # Add message
            state = add_message(
                state,
                agent="code_review",
                action="review_complete",
                data=review_result
            )

            logger.info(
                "code_review_complete",
                workflow_id=state["workflow_id"],
                approved=review_result["approved"]
            )

        except Exception as e:
            logger.error("code_review_failed", error=str(e))
            state["errors"].append(f"Code review failed: {str(e)}")

        return state

    def _test_generation_node(self, state: SDLCState) -> SDLCState:
        """
        Test generation agent node.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("test_generation_started", workflow_id=state["workflow_id"])

        try:
            # Generate tests
            test_result = self.test_generator_agent.generate_tests(
                code_changes=state["code_changes"],
                review_context=state["review_result"]
            )

            # Update state
            state = {
                **state,
                "test_result": test_result,
                "current_step": "test_generation_complete"
            }

            # Add message
            state = add_message(
                state,
                agent="test_generator",
                action="tests_generated",
                data=test_result
            )

            logger.info(
                "test_generation_complete",
                workflow_id=state["workflow_id"],
                test_count=len(test_result["tests_generated"])
            )

        except Exception as e:
            logger.error("test_generation_failed", error=str(e))
            state["errors"].append(f"Test generation failed: {str(e)}")

        return state

    def _deployment_node(self, state: SDLCState) -> SDLCState:
        """
        Deployment agent node.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("deployment_started", workflow_id=state["workflow_id"])

        try:
            # Deploy
            deployment_result = self.deployment_agent.deploy(
                code_changes=state["code_changes"],
                tests=state["test_result"]["tests_generated"],
                target=state["deployment_target"],
                dry_run=state["dry_run"]
            )

            # Update state
            state = {
                **state,
                "deployment_result": deployment_result,
                "current_step": "deployment_complete"
            }

            # Add message
            state = add_message(
                state,
                agent="deployment",
                action="deployment_complete",
                data=deployment_result
            )

            logger.info(
                "deployment_complete",
                workflow_id=state["workflow_id"],
                status=deployment_result["status"]
            )

        except Exception as e:
            logger.error("deployment_failed", error=str(e))
            state["errors"].append(f"Deployment failed: {str(e)}")

        return state

    def _feedback_node(self, state: SDLCState) -> SDLCState:
        """
        Feedback node for handling failures.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.warning("workflow_feedback", workflow_id=state["workflow_id"], errors=state["errors"])
        return state

    def _success_node(self, state: SDLCState) -> SDLCState:
        """
        Success node for completed workflows.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        from datetime import datetime

        state["completed_at"] = datetime.utcnow().isoformat()
        logger.info("workflow_success", workflow_id=state["workflow_id"])
        return state

    def _route_after_review(self, state: SDLCState) -> str:
        """
        Route after code review based on approval.

        Args:
            state: Current state

        Returns:
            Next node name
        """
        if state.get("review_result") and state["review_result"]["approved"]:
            return "test_generation"
        return "feedback"

    def _route_after_testing(self, state: SDLCState) -> str:
        """
        Route after test generation based on success.

        Args:
            state: Current state

        Returns:
            Next node name
        """
        if state.get("test_result") and state["test_result"]["runnable"]:
            return "deployment"
        return "feedback"

    def _route_after_deployment(self, state: SDLCState) -> str:
        """
        Route after deployment based on success.

        Args:
            state: Current state

        Returns:
            Next node name
        """
        if state.get("deployment_result") and state["deployment_result"]["status"] == "success":
            return "success"
        return "feedback"

    def process_changes(
        self,
        code_changes: str,
        target_branch: str = "main",
        deployment_target: str = "staging",
        dry_run: bool = True
    ) -> SDLCState:
        """
        Process code changes through the SDLC workflow.

        Args:
            code_changes: Path to code changes or diff content
            target_branch: Git branch to target
            deployment_target: Deployment environment
            dry_run: Whether to run in dry-run mode

        Returns:
            Final workflow state
        """
        # Create initial state
        initial_state = create_initial_state(
            code_changes=code_changes,
            target_branch=target_branch,
            deployment_target=deployment_target,
            dry_run=dry_run
        )

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        return final_state

    def stream_events(self, initial_state: SDLCState):
        """
        Stream workflow events as they occur.

        Args:
            initial_state: Initial workflow state

        Yields:
            Workflow events
        """
        for event in self.workflow.stream(initial_state):
            yield event
