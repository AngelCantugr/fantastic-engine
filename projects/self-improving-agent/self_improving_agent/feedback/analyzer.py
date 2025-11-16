"""
Feedback analysis module.
"""

from typing import Dict, Any, List
from collections import defaultdict, Counter
import structlog

logger = structlog.get_logger()


class FeedbackAnalyzer:
    """
    Analyzes feedback to identify improvement opportunities.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the feedback analyzer.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def analyze_failure(self, feedback: Any) -> Dict[str, Any]:
        """
        Analyze a failure case (low rating).

        Args:
            feedback: Feedback object

        Returns:
            Analysis dictionary
        """
        analysis = {
            "response_id": feedback.response_id,
            "rating": int(feedback.rating),
            "prompt_version": feedback.prompt_version,
            "strategy": feedback.strategy,
            "issues": []
        }

        # Analyze comment if provided
        if feedback.comment:
            issues = self._extract_issues_from_comment(feedback.comment)
            analysis["issues"].extend(issues)

        logger.info("failure_analyzed", response_id=feedback.response_id)

        return analysis

    def identify_patterns(self, responses: List[Any] = None) -> List[Dict[str, Any]]:
        """
        Identify patterns in feedback.

        Args:
            responses: Optional list of responses to analyze

        Returns:
            List of identified patterns
        """
        patterns = []

        # Pattern: Low ratings for specific prompt version
        version_ratings = defaultdict(list)
        strategy_ratings = defaultdict(list)

        # This is a simplified implementation
        # In production, would do more sophisticated pattern detection

        patterns.append({
            "type": "version_performance",
            "description": "Performance varies by prompt version",
            "suggestion": "Consider testing new prompt variations"
        })

        logger.info("patterns_identified", count=len(patterns))

        return patterns

    def _extract_issues_from_comment(self, comment: str) -> List[str]:
        """
        Extract issues from a comment.

        Args:
            comment: Feedback comment

        Returns:
            List of issues
        """
        issues = []

        # Simple keyword-based extraction
        keywords = {
            "too long": "response_too_verbose",
            "too short": "response_too_brief",
            "incorrect": "factual_error",
            "unclear": "clarity_issue",
            "confusing": "clarity_issue"
        }

        comment_lower = comment.lower()

        for keyword, issue in keywords.items():
            if keyword in comment_lower:
                issues.append(issue)

        return issues
