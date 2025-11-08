"""
Rule-based Data Validation using Great Expectations

Wrapper around Great Expectations for structured validation.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from loguru import logger


class GreatExpectationsValidator:
    """
    Rule-based validator using Great Expectations.

    Examples:
        >>> validator = GreatExpectationsValidator()
        >>> results = validator.validate(df, expectations)
    """

    def __init__(self):
        """Initialize Great Expectations validator."""
        logger.info("Initialized GreatExpectationsValidator")

    def validate_from_config(
        self,
        df: pd.DataFrame,
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate DataFrame using rules from configuration.

        Args:
            df: DataFrame to validate
            rules: List of validation rules

        Returns:
            Validation results
        """
        results = {
            'success': True,
            'results': [],
            'statistics': {}
        }

        for rule in rules:
            column = rule['column']
            expectations = rule.get('expectations', [])

            for expectation in expectations:
                result = self._run_expectation(
                    df, column, expectation
                )
                results['results'].append(result)

                if not result['success']:
                    results['success'] = False

        # Calculate statistics
        results['statistics'] = {
            'total_expectations': len(results['results']),
            'successful_expectations': sum(
                1 for r in results['results'] if r['success']
            ),
            'failed_expectations': sum(
                1 for r in results['results'] if not r['success']
            )
        }

        return results

    def _run_expectation(
        self,
        df: pd.DataFrame,
        column: str,
        expectation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single expectation."""
        exp_type = expectation['type']

        try:
            if exp_type == 'expect_column_values_to_be_between':
                return self._validate_between(
                    df, column,
                    expectation['min'],
                    expectation['max'],
                    expectation.get('mostly', 1.0)
                )

            elif exp_type == 'expect_column_values_to_not_be_null':
                return self._validate_not_null(df, column)

            elif exp_type == 'expect_column_values_to_be_in_set':
                return self._validate_in_set(
                    df, column,
                    expectation.get('value_set', expectation.get('values', []))
                )

            else:
                return {
                    'success': False,
                    'expectation_type': exp_type,
                    'column': column,
                    'error': f'Unsupported expectation type: {exp_type}'
                }

        except Exception as e:
            logger.error(f"Expectation failed: {e}")
            return {
                'success': False,
                'expectation_type': exp_type,
                'column': column,
                'error': str(e)
            }

    def _validate_between(
        self,
        df: pd.DataFrame,
        column: str,
        min_val: float,
        max_val: float,
        mostly: float = 1.0
    ) -> Dict[str, Any]:
        """Validate column values are between min and max."""
        if column not in df.columns:
            return {
                'success': False,
                'expectation_type': 'expect_column_values_to_be_between',
                'column': column,
                'error': f'Column {column} not found'
            }

        series = df[column].dropna()
        in_range = series.between(min_val, max_val)
        pct_in_range = in_range.sum() / len(series) if len(series) > 0 else 0

        success = pct_in_range >= mostly

        return {
            'success': success,
            'expectation_type': 'expect_column_values_to_be_between',
            'column': column,
            'result': {
                'observed_value': pct_in_range,
                'min_value': min_val,
                'max_value': max_val,
                'mostly': mostly,
                'out_of_range_count': (~in_range).sum()
            }
        }

    def _validate_not_null(
        self,
        df: pd.DataFrame,
        column: str
    ) -> Dict[str, Any]:
        """Validate column has no null values."""
        if column not in df.columns:
            return {
                'success': False,
                'expectation_type': 'expect_column_values_to_not_be_null',
                'column': column,
                'error': f'Column {column} not found'
            }

        null_count = df[column].isnull().sum()
        success = null_count == 0

        return {
            'success': success,
            'expectation_type': 'expect_column_values_to_not_be_null',
            'column': column,
            'result': {
                'null_count': int(null_count),
                'null_percent': (null_count / len(df)) * 100
            }
        }

    def _validate_in_set(
        self,
        df: pd.DataFrame,
        column: str,
        value_set: List[Any]
    ) -> Dict[str, Any]:
        """Validate column values are in allowed set."""
        if column not in df.columns:
            return {
                'success': False,
                'expectation_type': 'expect_column_values_to_be_in_set',
                'column': column,
                'error': f'Column {column} not found'
            }

        series = df[column].dropna()
        in_set = series.isin(value_set)
        pct_in_set = in_set.sum() / len(series) if len(series) > 0 else 0

        success = pct_in_set == 1.0

        unexpected_values = series[~in_set].unique().tolist()

        return {
            'success': success,
            'expectation_type': 'expect_column_values_to_be_in_set',
            'column': column,
            'result': {
                'observed_percent': pct_in_set,
                'value_set': value_set,
                'unexpected_values': unexpected_values[:10],  # Limit to 10
                'unexpected_count': len(unexpected_values)
            }
        }
