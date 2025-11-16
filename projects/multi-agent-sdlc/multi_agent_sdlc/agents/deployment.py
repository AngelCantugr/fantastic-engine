"""
Deployment Agent - Handles safe deployment with rollback capability.
"""

from typing import Dict, Any, List
from multi_agent_sdlc.agents.base import BaseAgent
from multi_agent_sdlc.state import DeploymentResult, DeploymentStatus
from datetime import datetime
import json
import structlog

logger = structlog.get_logger()


class DeploymentAgent(BaseAgent):
    """
    Agent responsible for safe deployment.

    Performs:
    - Safety checks
    - Breaking change detection
    - Dependency conflict detection
    - Resource usage estimation
    - Deployment with rollback capability
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Deployment Agent.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.enable_auto_deployment = self.config.get("enable_auto_deployment", False)

    def get_system_prompt(self) -> str:
        """Get the system prompt for deployment analysis."""
        return """You are an expert DevOps engineer specializing in safe deployments.

Your task is to analyze code changes and determine deployment safety, including:
1. Breaking change detection
2. Dependency conflict detection
3. Resource usage estimation
4. Backward compatibility analysis
5. Rollback strategy

Perform comprehensive safety checks and provide:
- Deployment recommendation (safe/unsafe)
- Identified risks and mitigation strategies
- Rollback plan
- Health check suggestions

Return your analysis in JSON format:
{
    "safe_to_deploy": boolean,
    "risks": [
        {
            "category": "breaking_change|dependency|resource|compatibility",
            "severity": "low|medium|high|critical",
            "description": "risk description",
            "mitigation": "how to mitigate"
        }
    ],
    "rollback_plan": "rollback strategy description",
    "health_checks": ["check 1", "check 2"],
    "estimated_downtime": "none|minimal|moderate",
    "notes": ["deployment note 1"]
}
"""

    def get_user_prompt_template(self) -> str:
        """Get the user prompt template for deployment analysis."""
        return """Analyze the following code changes for deployment safety:

{code_changes}

Tests Generated:
{tests}

Target Environment: {target}
Dry Run Mode: {dry_run}

Provide a comprehensive deployment safety analysis in the specified JSON format."""

    def deploy(
        self,
        code_changes: str,
        tests: List[str],
        target: str = "staging",
        dry_run: bool = True
    ) -> DeploymentResult:
        """
        Perform deployment with safety checks.

        Args:
            code_changes: Code changes to deploy
            tests: Generated tests
            target: Target environment (staging/production)
            dry_run: Whether to run in dry-run mode

        Returns:
            DeploymentResult with deployment details
        """
        logger.info(
            "starting_deployment",
            target=target,
            dry_run=dry_run,
            test_count=len(tests)
        )

        try:
            # Create prompt
            prompt = self.create_prompt()

            # Invoke LLM for safety analysis
            response = self.invoke_llm(
                prompt,
                code_changes=code_changes,
                tests="\n".join(tests[:5]),  # Include first 5 tests as context
                target=target,
                dry_run=str(dry_run)
            )

            # Parse response
            try:
                safety_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                logger.warning("invalid_json_response", response=response[:200])
                safety_data = {
                    "safe_to_deploy": False,
                    "risks": [{
                        "category": "compatibility",
                        "severity": "high",
                        "description": "Could not parse safety analysis",
                        "mitigation": "Manual review required"
                    }],
                    "rollback_plan": "Manual rollback required",
                    "health_checks": [],
                    "estimated_downtime": "unknown",
                    "notes": ["Safety analysis failed"]
                }

            # Determine deployment status
            if dry_run:
                status = DeploymentStatus.SUCCESS  # Dry run always succeeds
            elif safety_data.get("safe_to_deploy", False):
                # In real implementation, this would trigger actual deployment
                status = DeploymentStatus.SUCCESS
            else:
                status = DeploymentStatus.FAILED

            # Create DeploymentResult
            result = DeploymentResult(
                status=status,
                target_environment=target,
                artifacts=[],  # Would include actual deployment artifacts
                health_check_passed=safety_data.get("safe_to_deploy", False),
                rollback_available=True,
                timestamp=datetime.utcnow().isoformat()
            )

            logger.info(
                "deployment_complete",
                status=result["status"],
                target=target,
                dry_run=dry_run,
                safe_to_deploy=safety_data.get("safe_to_deploy", False)
            )

            return result

        except Exception as e:
            logger.error("deployment_error", error=str(e))
            # Return a safe failure result
            return DeploymentResult(
                status=DeploymentStatus.FAILED,
                target_environment=target,
                artifacts=[],
                health_check_passed=False,
                rollback_available=True,
                timestamp=datetime.utcnow().isoformat()
            )

    def rollback(self, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback a deployment.

        Args:
            deployment_id: ID of deployment to rollback

        Returns:
            Rollback result
        """
        logger.info("initiating_rollback", deployment_id=deployment_id)

        # In real implementation, this would trigger actual rollback
        return {
            "status": "success",
            "deployment_id": deployment_id,
            "timestamp": datetime.utcnow().isoformat()
        }
