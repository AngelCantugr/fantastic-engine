"""
Test Generator Agent - Generates tests for code changes.
"""

from typing import Dict, Any, Optional
from multi_agent_sdlc.agents.base import BaseAgent
from multi_agent_sdlc.state import TestResult, ReviewResult
from datetime import datetime
import json
import structlog

logger = structlog.get_logger()


class TestGeneratorAgent(BaseAgent):
    """
    Agent responsible for generating tests for code changes.

    Generates:
    - Unit tests
    - Integration tests
    - Edge case tests
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Test Generator Agent.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.coverage_target = self.config.get("coverage_target", 80)
        self.test_frameworks = self.config.get("test_frameworks", ["pytest"])

    def get_system_prompt(self) -> str:
        """Get the system prompt for test generation."""
        return """You are an expert test engineer specializing in comprehensive test coverage.

Your task is to generate high-quality tests for code changes, including:
1. Unit tests for individual functions/methods
2. Integration tests for component interactions
3. Edge case tests for boundary conditions
4. Security tests for vulnerabilities
5. Performance tests if applicable

Generate tests that:
- Follow testing best practices
- Use appropriate testing frameworks
- Are runnable without modification
- Cover both happy paths and error cases
- Include clear test names and descriptions

Return your analysis in JSON format:
{
    "tests_generated": [
        "test code block 1",
        "test code block 2"
    ],
    "coverage_estimate": 85.5,
    "framework": "pytest",
    "runnable": true,
    "notes": ["note about test approach"]
}
"""

    def get_user_prompt_template(self) -> str:
        """Get the user prompt template for test generation."""
        return """Generate comprehensive tests for the following code changes:

{code_changes}

Review Context:
{review_context}

Coverage Target: {coverage_target}%
Preferred Frameworks: {test_frameworks}

Generate tests in the specified JSON format."""

    def generate_tests(
        self,
        code_changes: str,
        review_context: Optional[ReviewResult] = None
    ) -> TestResult:
        """
        Generate tests for code changes.

        Args:
            code_changes: Code changes to generate tests for
            review_context: Optional review context for better test generation

        Returns:
            TestResult with generated tests
        """
        logger.info("starting_test_generation", coverage_target=self.coverage_target)

        try:
            # Create prompt
            prompt = self.create_prompt()

            # Format review context
            review_str = "No review context available"
            if review_context:
                review_str = f"""
Approved: {review_context['approved']}
Issues Found: {len(review_context['issues'])}
Comments: {', '.join(review_context['comments'][:3])}
"""

            # Invoke LLM
            response = self.invoke_llm(
                prompt,
                code_changes=code_changes,
                review_context=review_str,
                coverage_target=self.coverage_target,
                test_frameworks=", ".join(self.test_frameworks)
            )

            # Parse response
            try:
                test_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                logger.warning("invalid_json_response", response=response[:200])
                test_data = {
                    "tests_generated": [],
                    "coverage_estimate": 0.0,
                    "framework": self.test_frameworks[0],
                    "runnable": False,
                    "notes": ["Failed to parse test generation response"]
                }

            # Create TestResult
            result = TestResult(
                tests_generated=test_data.get("tests_generated", []),
                coverage_estimate=test_data.get("coverage_estimate", 0.0),
                framework=test_data.get("framework", self.test_frameworks[0]),
                runnable=test_data.get("runnable", False),
                timestamp=datetime.utcnow().isoformat()
            )

            logger.info(
                "test_generation_complete",
                test_count=len(result["tests_generated"]),
                coverage=result["coverage_estimate"],
                runnable=result["runnable"]
            )

            return result

        except Exception as e:
            logger.error("test_generation_error", error=str(e))
            # Return a safe failure result
            return TestResult(
                tests_generated=[],
                coverage_estimate=0.0,
                framework=self.test_frameworks[0] if self.test_frameworks else "pytest",
                runnable=False,
                timestamp=datetime.utcnow().isoformat()
            )
