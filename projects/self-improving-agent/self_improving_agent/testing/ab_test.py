"""
A/B testing framework for comparing strategies.
"""

from typing import Dict, Any
from dataclasses import dataclass
from scipy import stats
import structlog

logger = structlog.get_logger()


@dataclass
class ABTestResult:
    """A/B test result."""
    winner: str
    variant_a_score: float
    variant_b_score: float
    confidence: float
    p_value: float
    sample_size: int


class ABTestRunner:
    """
    Runs A/B tests to compare strategies.
    """

    def __init__(
        self,
        name: str,
        variants: Dict[str, Any],
        config: Dict[str, Any] = None
    ):
        """
        Initialize the A/B test runner.

        Args:
            name: Test name
            variants: Dictionary of variant_name -> variant_config
            config: Configuration dictionary
        """
        self.name = name
        self.variants = variants
        self.config = config or {}
        self.min_confidence = self.config.get("min_confidence_level", 0.95)

        self.variant_results = {name: [] for name in variants.keys()}

    def record_result(self, variant_name: str, rating: float):
        """
        Record a result for a variant.

        Args:
            variant_name: Name of variant
            rating: Rating received
        """
        if variant_name not in self.variant_results:
            raise ValueError(f"Unknown variant: {variant_name}")

        self.variant_results[variant_name].append(rating)

        logger.info(
            "ab_test_result_recorded",
            test=self.name,
            variant=variant_name,
            rating=rating
        )

    def run(self, sample_size: int) -> ABTestResult:
        """
        Run the A/B test.

        Args:
            sample_size: Minimum sample size per variant

        Returns:
            ABTestResult
        """
        logger.info("running_ab_test", test=self.name, sample_size=sample_size)

        # Simplified implementation - assumes we already have results
        # In production, would actually run the test and collect results

        variant_names = list(self.variants.keys())
        variant_a = variant_names[0]
        variant_b = variant_names[1] if len(variant_names) > 1 else variant_names[0]

        # Mock results for demonstration
        results_a = self.variant_results.get(variant_a, [4.0] * sample_size)
        results_b = self.variant_results.get(variant_b, [3.5] * sample_size)

        # Calculate statistics
        mean_a = sum(results_a) / len(results_a) if results_a else 0
        mean_b = sum(results_b) / len(results_b) if results_b else 0

        # Perform t-test
        if len(results_a) > 1 and len(results_b) > 1:
            t_stat, p_value = stats.ttest_ind(results_a, results_b)
            confidence = 1 - p_value
        else:
            p_value = 1.0
            confidence = 0.0

        # Determine winner
        winner = variant_a if mean_a > mean_b else variant_b

        result = ABTestResult(
            winner=winner,
            variant_a_score=mean_a,
            variant_b_score=mean_b,
            confidence=confidence,
            p_value=p_value,
            sample_size=len(results_a)
        )

        logger.info(
            "ab_test_complete",
            test=self.name,
            winner=winner,
            confidence=confidence
        )

        return result
