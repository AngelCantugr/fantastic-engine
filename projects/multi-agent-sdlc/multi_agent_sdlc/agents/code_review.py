"""
Code Review Agent - Analyzes code changes for quality, security, and best practices.
"""

from typing import Dict, Any
from multi_agent_sdlc.agents.base import BaseAgent
from multi_agent_sdlc.state import ReviewResult, ReviewSeverity
from datetime import datetime
import json
import structlog

logger = structlog.get_logger()


class CodeReviewAgent(BaseAgent):
    """
    Agent responsible for reviewing code changes.

    Analyzes code for:
    - Code quality and style
    - Security vulnerabilities
    - Performance issues
    - Best practices violations
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Code Review Agent.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.severity_threshold = self.config.get("severity_threshold", "warning")
        self.custom_rules = self.config.get("custom_rules", [])

    def get_system_prompt(self) -> str:
        """Get the system prompt for code review."""
        return """You are an expert code reviewer with deep knowledge of software engineering best practices,
security vulnerabilities, and performance optimization.

Your task is to review code changes and provide:
1. Overall assessment (approve/reject)
2. Specific issues found with severity levels (info, warning, error, critical)
3. Detailed comments and suggestions
4. Security vulnerability analysis
5. Performance considerations

Be thorough but constructive. Focus on actual issues, not nitpicking.

Return your analysis in JSON format:
{
    "approved": boolean,
    "severity": "info|warning|error|critical",
    "issues": [
        {
            "line": number or null,
            "severity": "info|warning|error|critical",
            "category": "security|performance|quality|style",
            "message": "description",
            "suggestion": "how to fix"
        }
    ],
    "comments": ["general comment 1", "general comment 2"]
}
"""

    def get_user_prompt_template(self) -> str:
        """Get the user prompt template for code review."""
        return """Please review the following code changes:

{code_changes}

Target Branch: {target_branch}
Severity Threshold: {severity_threshold}

Custom Rules to Check:
{custom_rules}

Provide a detailed code review in the specified JSON format."""

    def review(self, code_changes: str, target_branch: str = "main") -> ReviewResult:
        """
        Review code changes.

        Args:
            code_changes: Code changes (diff or file content)
            target_branch: Target branch for the changes

        Returns:
            ReviewResult with review details
        """
        logger.info("starting_code_review", target_branch=target_branch)

        try:
            # Create prompt
            prompt = self.create_prompt()

            # Invoke LLM
            response = self.invoke_llm(
                prompt,
                code_changes=code_changes,
                target_branch=target_branch,
                severity_threshold=self.severity_threshold,
                custom_rules="\n".join(self.custom_rules) if self.custom_rules else "None"
            )

            # Parse response
            try:
                review_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                logger.warning("invalid_json_response", response=response[:200])
                review_data = {
                    "approved": False,
                    "severity": "error",
                    "issues": [{
                        "line": None,
                        "severity": "error",
                        "category": "quality",
                        "message": "Could not parse review response",
                        "suggestion": "Manual review required"
                    }],
                    "comments": ["Automated review failed - manual review required"]
                }

            # Create ReviewResult
            result = ReviewResult(
                approved=review_data.get("approved", False),
                severity=ReviewSeverity(review_data.get("severity", "warning")),
                issues=review_data.get("issues", []),
                comments=review_data.get("comments", []),
                timestamp=datetime.utcnow().isoformat()
            )

            logger.info(
                "code_review_complete",
                approved=result["approved"],
                issue_count=len(result["issues"]),
                severity=result["severity"]
            )

            return result

        except Exception as e:
            logger.error("code_review_error", error=str(e))
            # Return a safe failure result
            return ReviewResult(
                approved=False,
                severity=ReviewSeverity.ERROR,
                issues=[{
                    "line": None,
                    "severity": "error",
                    "category": "quality",
                    "message": f"Review failed: {str(e)}",
                    "suggestion": "Manual review required"
                }],
                comments=[f"Automated review encountered an error: {str(e)}"],
                timestamp=datetime.utcnow().isoformat()
            )
