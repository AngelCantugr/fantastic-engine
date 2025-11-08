"""
AI-Powered Anomaly Explainer

Uses LLMs to explain data anomalies in human-readable language
and suggest actionable fixes.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from loguru import logger
from ..utils.llm_client import LLMClient


class AnomalyExplainer:
    """
    Explains data anomalies using LLMs.

    Examples:
        >>> explainer = AnomalyExplainer(llm_provider="anthropic")
        >>> explanation = explainer.explain_anomaly(
        ...     column="fare_amount",
        ...     anomaly_type="negative_values",
        ...     samples=negative_fares_df
        ... )
    """

    def __init__(
        self,
        llm_provider: str = "anthropic",
        llm_model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize anomaly explainer.

        Args:
            llm_provider: LLM provider ("anthropic" or "openai")
            llm_model: Specific model to use
            temperature: LLM temperature (lower = more focused)
        """
        self.llm = LLMClient(
            provider=llm_provider,
            model=llm_model,
            temperature=temperature
        )
        logger.info(f"Initialized AnomalyExplainer with {llm_provider}")

    def explain_anomaly(
        self,
        column: str,
        anomaly_type: str,
        samples: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None,
        max_samples: int = 10
    ) -> Dict[str, Any]:
        """
        Generate explanation for a detected anomaly.

        Args:
            column: Column name where anomaly was detected
            anomaly_type: Type of anomaly (e.g., "outliers", "nulls", "duplicates")
            samples: DataFrame with sample anomalous rows
            context: Additional context about the dataset
            max_samples: Maximum number of sample rows to include

        Returns:
            Dictionary with:
                - explanation: Human-readable explanation
                - likely_causes: List of probable causes
                - suggested_fixes: List of recommended fixes
                - severity: Severity level (low/medium/high/critical)
        """
        # Prepare samples summary
        samples_summary = self._summarize_samples(samples, max_samples)

        # Build prompt
        prompt = self._build_anomaly_prompt(
            column=column,
            anomaly_type=anomaly_type,
            samples_summary=samples_summary,
            context=context or {}
        )

        # Generate explanation
        response = self.llm.generate_structured(
            prompt=prompt,
            schema={
                "explanation": "string - detailed explanation",
                "likely_causes": ["array of probable causes"],
                "suggested_fixes": ["array of recommended fixes with code examples"],
                "severity": "string - low/medium/high/critical",
                "confidence": "number - 0-100"
            },
            system_prompt="You are a data quality expert specializing in identifying and explaining data anomalies."
        )

        return response

    def explain_outliers(
        self,
        column: str,
        outliers: pd.DataFrame,
        statistics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Specialized explanation for outliers.

        Args:
            column: Column with outliers
            outliers: DataFrame with outlier rows
            statistics: Statistical summary (mean, std, median, etc.)
            context: Dataset context

        Returns:
            Structured explanation
        """
        prompt = f"""
Analyze these OUTLIERS in column '{column}':

STATISTICS:
- Mean: {statistics.get('mean', 'N/A')}
- Median: {statistics.get('median', 'N/A')}
- Std Dev: {statistics.get('std', 'N/A')}
- Min: {statistics.get('min', 'N/A')}
- Max: {statistics.get('max', 'N/A')}
- 99th percentile: {statistics.get('p99', 'N/A')}

OUTLIER SAMPLES (first 10):
{outliers.head(10).to_string()}

DATASET CONTEXT:
{context or 'No additional context provided'}

Explain:
1. Why these are outliers (statistical vs. business logic)
2. Are they legitimate extreme values or data errors?
3. What should be done with them (keep/remove/cap/investigate)?
"""

        return self.llm.generate_structured(
            prompt=prompt,
            schema={
                "outlier_type": "string - 'legitimate_extreme' or 'data_error' or 'unclear'",
                "explanation": "string",
                "evidence": ["array of evidence supporting the classification"],
                "recommended_action": "string - keep/remove/cap/flag_for_review",
                "threshold_suggestion": "string - suggested threshold if capping"
            }
        )

    def explain_missing_values(
        self,
        column: str,
        missing_count: int,
        total_count: int,
        sample_rows: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Explain missing/null values pattern.

        Args:
            column: Column with missing values
            missing_count: Number of missing values
            total_count: Total rows
            sample_rows: Sample of rows with missing values
            context: Dataset context

        Returns:
            Structured explanation
        """
        missing_pct = (missing_count / total_count) * 100

        prompt = f"""
Analyze MISSING VALUES in column '{column}':

STATISTICS:
- Missing: {missing_count:,} / {total_count:,} ({missing_pct:.2f}%)

SAMPLE ROWS WITH MISSING VALUES:
{sample_rows.head(10).to_string()}

CONTEXT:
{context or 'No additional context'}

Explain:
1. Why are values missing? (random, systematic, expected)
2. Is the missing rate acceptable?
3. How should missing values be handled?
"""

        return self.llm.generate_structured(
            prompt=prompt,
            schema={
                "missing_pattern": "string - random/systematic/expected",
                "explanation": "string",
                "acceptability": "string - acceptable/concerning/critical",
                "recommended_strategy": "string - drop/impute_mean/impute_median/forward_fill/model_based/leave_as_null",
                "reasoning": "string"
            }
        )

    def explain_data_drift(
        self,
        column: str,
        reference_stats: Dict[str, float],
        current_stats: Dict[str, float],
        drift_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Explain detected data drift.

        Args:
            column: Column where drift was detected
            reference_stats: Statistics from reference dataset
            current_stats: Statistics from current dataset
            drift_score: Numerical drift score
            context: Additional context

        Returns:
            Structured explanation of drift
        """
        prompt = f"""
Analyze DATA DRIFT in column '{column}':

REFERENCE (baseline) STATISTICS:
{reference_stats}

CURRENT STATISTICS:
{current_stats}

DRIFT SCORE: {drift_score:.4f}

CONTEXT:
{context or 'No additional context'}

Explain:
1. What changed between reference and current data?
2. Is this drift expected (seasonal, business change) or concerning (data quality issue)?
3. What actions should be taken?
"""

        return self.llm.generate_structured(
            prompt=prompt,
            schema={
                "drift_type": "string - distribution_shift/mean_shift/variance_change/range_change",
                "severity": "string - low/medium/high/critical",
                "explanation": "string",
                "likely_cause": "string",
                "expected_vs_unexpected": "string - expected/unexpected",
                "recommended_actions": ["array of actions"]
            }
        )

    def batch_explain_anomalies(
        self,
        anomalies: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Explain multiple anomalies efficiently.

        Args:
            anomalies: List of anomaly dicts with 'column', 'type', 'samples'
            context: Shared context

        Returns:
            List of explanations
        """
        # Could optimize with batching in future
        explanations = []

        for anomaly in anomalies:
            try:
                explanation = self.explain_anomaly(
                    column=anomaly['column'],
                    anomaly_type=anomaly['type'],
                    samples=anomaly.get('samples', pd.DataFrame()),
                    context=context
                )
                explanations.append(explanation)
            except Exception as e:
                logger.error(f"Failed to explain anomaly in {anomaly['column']}: {e}")
                explanations.append({
                    "error": str(e),
                    "column": anomaly['column']
                })

        return explanations

    def _summarize_samples(self, samples: pd.DataFrame, max_samples: int) -> str:
        """Create a concise summary of sample rows."""
        if samples.empty:
            return "No samples available"

        # Limit to max_samples rows
        limited = samples.head(max_samples)

        # Create summary
        summary = f"Sample rows ({len(limited)} of {len(samples)} total):\n"
        summary += limited.to_string(index=False)

        return summary

    def _build_anomaly_prompt(
        self,
        column: str,
        anomaly_type: str,
        samples_summary: str,
        context: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for anomaly explanation."""
        prompt = f"""
Analyze this DATA ANOMALY:

COLUMN: {column}
ANOMALY TYPE: {anomaly_type}

{samples_summary}

DATASET CONTEXT:
- Dataset: {context.get('dataset', 'Unknown')}
- Domain: {context.get('domain', 'Unknown')}
- Date Range: {context.get('date_range', 'Unknown')}
- Additional Info: {context.get('notes', 'None')}

Provide:
1. Clear explanation of what this anomaly means
2. Most likely root causes
3. Concrete suggested fixes (with code/SQL examples if applicable)
4. Severity assessment
"""
        return prompt


# Convenience functions
def explain_outliers_quick(
    column: str,
    outliers: pd.DataFrame,
    statistics: Dict[str, float]
) -> str:
    """Quick outlier explanation (returns text only)."""
    explainer = AnomalyExplainer()
    result = explainer.explain_outliers(column, outliers, statistics)
    return result.get('explanation', 'No explanation generated')
