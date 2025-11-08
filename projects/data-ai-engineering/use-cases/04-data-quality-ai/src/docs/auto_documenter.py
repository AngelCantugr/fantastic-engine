"""
Automatic Documentation Generator

Uses LLMs to generate human-readable documentation from data and validation results.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path
from loguru import logger
from ..utils.llm_client import LLMClient


class AutoDocumenter:
    """
    Automatically generates data documentation using LLMs.

    Creates:
    - Data dictionaries (column descriptions)
    - Quality reports
    - Schema documentation
    - Example queries

    Examples:
        >>> documenter = AutoDocumenter()
        >>> docs = documenter.generate_full_documentation(
        ...     dataset_path="data/nyc_taxi.parquet",
        ...     validation_results=results
        ... )
    """

    def __init__(
        self,
        llm_provider: str = "anthropic",
        llm_model: Optional[str] = None,
        output_format: str = "markdown"
    ):
        """
        Initialize auto-documenter.

        Args:
            llm_provider: LLM provider
            llm_model: Specific model
            output_format: Output format (markdown, html, rst)
        """
        self.llm = LLMClient(provider=llm_provider, model=llm_model)
        self.output_format = output_format
        logger.info(f"Initialized AutoDocumenter with {llm_provider}")

    def generate_full_documentation(
        self,
        dataset_path: str,
        validation_results: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate complete documentation for a dataset.

        Args:
            dataset_path: Path to dataset
            validation_results: Optional validation results to include
            output_path: Where to save documentation

        Returns:
            Generated documentation as string
        """
        # Load data
        df = self._load_dataset(dataset_path)

        # Generate components
        overview = self.generate_overview(df, dataset_path)
        data_dict = self.generate_data_dictionary(df)
        statistics = self.generate_statistics_summary(df)
        quality_report = self.generate_quality_report(validation_results) \
            if validation_results else ""
        example_queries = self.generate_example_queries(df)

        # Combine into full document
        full_doc = self._combine_sections([
            ("# Dataset Documentation", ""),
            ("## Overview", overview),
            ("## Data Dictionary", data_dict),
            ("## Statistical Summary", statistics),
            ("## Data Quality Report", quality_report),
            ("## Example Queries", example_queries)
        ])

        # Save if output path provided
        if output_path:
            Path(output_path).write_text(full_doc)
            logger.info(f"Documentation saved to {output_path}")

        return full_doc

    def generate_data_dictionary(self, df: pd.DataFrame) -> str:
        """
        Generate data dictionary with AI-inferred column descriptions.

        Args:
            df: Input DataFrame

        Returns:
            Data dictionary as markdown table
        """
        # Get column information
        column_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            sample_values = df[col].dropna().head(5).tolist()

            column_info.append({
                'name': col,
                'type': dtype,
                'null_pct': f"{null_pct:.2f}%",
                'unique_count': unique_count,
                'samples': sample_values
            })

        # Generate descriptions using LLM
        prompt = f"""
Generate concise, technical descriptions for these data columns.
For each column, provide a 1-2 sentence description of what it represents.

COLUMNS:
{self._format_column_info(column_info)}

Return as JSON array:
[
  {{"column": "name", "description": "Human-readable description"}},
  ...
]
"""

        descriptions = self.llm.generate_structured(
            prompt=prompt,
            schema={"columns": [{"column": "string", "description": "string"}]},
            system_prompt="You are a data documentation specialist."
        )

        # Build markdown table
        table = "| Column | Type | Null % | Unique | Description |\n"
        table += "|--------|------|--------|--------|-------------|\n"

        desc_map = {d['column']: d['description']
                    for d in descriptions.get('columns', [])}

        for info in column_info:
            desc = desc_map.get(info['name'], 'No description')
            table += f"| {info['name']} | {info['type']} | {info['null_pct']} | " \
                     f"{info['unique_count']} | {desc} |\n"

        return table

    def generate_overview(
        self,
        df: pd.DataFrame,
        dataset_path: str
    ) -> str:
        """Generate high-level dataset overview."""
        prompt = f"""
Generate a concise overview for this dataset.

DATASET INFO:
- Path: {dataset_path}
- Rows: {len(df):,}
- Columns: {len(df.columns)}
- Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
- Column names: {', '.join(df.columns.tolist())}

Write 2-3 paragraphs covering:
1. What this dataset appears to contain
2. Primary use cases
3. Key characteristics
"""

        overview = self.llm.generate(prompt)
        return overview

    def generate_statistics_summary(self, df: pd.DataFrame) -> str:
        """Generate statistical summary with insights."""
        # Get basic statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        stats_df = df[numeric_cols].describe()

        prompt = f"""
Analyze these statistics and highlight key insights:

{stats_df.to_string()}

Provide:
1. Key statistics worth noting
2. Interesting patterns
3. Potential concerns
"""

        insights = self.llm.generate(prompt)

        # Format as markdown
        summary = "### Basic Statistics\n\n"
        summary += f"```\n{stats_df.to_string()}\n```\n\n"
        summary += "### Key Insights\n\n"
        summary += insights

        return summary

    def generate_quality_report(
        self,
        validation_results: Dict[str, Any]
    ) -> str:
        """
        Generate quality report from validation results.

        Args:
            validation_results: Results from data validation

        Returns:
            Quality report as markdown
        """
        prompt = f"""
Create a data quality report summary from these validation results:

{validation_results}

Include:
1. Overall quality score/status
2. Critical issues (if any)
3. Warnings
4. Recommendations
"""

        report = self.llm.generate(prompt)
        return report

    def generate_example_queries(self, df: pd.DataFrame) -> str:
        """
        Generate example SQL/Pandas queries for common operations.

        Args:
            df: Input DataFrame

        Returns:
            Example queries as markdown
        """
        # Sample column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()[:3]
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()[:3]
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()[:2]

        prompt = f"""
Generate 5-10 useful example queries for this dataset.

COLUMN TYPES:
- Numeric: {numeric_cols}
- Categorical: {categorical_cols}
- Date/Time: {date_cols}

Provide both SQL and Pandas versions for:
1. Basic filtering
2. Aggregations
3. Grouping
4. Window functions (if date columns exist)
5. Joins (if applicable)

Format as markdown with code blocks.
"""

        examples = self.llm.generate(prompt)
        return examples

    def generate_schema_doc(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate schema documentation in structured format.

        Args:
            df: Input DataFrame

        Returns:
            Schema documentation as dict
        """
        schema_info = []
        for col in df.columns:
            schema_info.append({
                "name": col,
                "type": str(df[col].dtype),
                "nullable": bool(df[col].isnull().any()),
                "unique_count": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(3).tolist()
            })

        prompt = f"""
Enhance this schema documentation with:
1. Inferred semantic types (email, phone, id, etc.)
2. Validation rules
3. Relationships between columns

SCHEMA:
{schema_info}

Return as enhanced JSON.
"""

        enhanced_schema = self.llm.generate_structured(
            prompt=prompt,
            schema={
                "columns": [{
                    "name": "string",
                    "type": "string",
                    "semantic_type": "string",
                    "validation_rules": ["array"],
                    "related_columns": ["array"]
                }]
            }
        )

        return enhanced_schema

    def generate_changelog(
        self,
        old_df: pd.DataFrame,
        new_df: pd.DataFrame
    ) -> str:
        """
        Generate changelog between two dataset versions.

        Args:
            old_df: Previous version
            new_df: Current version

        Returns:
            Changelog as markdown
        """
        # Detect changes
        changes = self._detect_schema_changes(old_df, new_df)

        prompt = f"""
Generate a changelog summary for dataset updates:

CHANGES DETECTED:
{changes}

Format as:
## Schema Changes
- Added columns: ...
- Removed columns: ...
- Type changes: ...

## Data Changes
- Row count: old vs new
- Key differences
"""

        changelog = self.llm.generate(prompt)
        return changelog

    # Helper methods

    def _load_dataset(self, path: str) -> pd.DataFrame:
        """Load dataset from various formats."""
        path = Path(path)

        if path.suffix == '.parquet':
            return pd.read_parquet(path)
        elif path.suffix == '.csv':
            return pd.read_csv(path)
        elif path.suffix == '.json':
            return pd.read_json(path)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")

    def _format_column_info(self, column_info: List[Dict]) -> str:
        """Format column info for LLM prompt."""
        formatted = []
        for col in column_info:
            formatted.append(
                f"- {col['name']} ({col['type']}): "
                f"{col['unique_count']} unique values, "
                f"{col['null_pct']} null, "
                f"samples: {col['samples']}"
            )
        return "\n".join(formatted)

    def _combine_sections(self, sections: List[tuple]) -> str:
        """Combine documentation sections."""
        output = []
        for title, content in sections:
            if content:  # Only include non-empty sections
                output.append(f"{title}\n\n{content}\n\n")
        return "\n".join(output)

    def _detect_schema_changes(
        self,
        old_df: pd.DataFrame,
        new_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Detect schema changes between versions."""
        old_cols = set(old_df.columns)
        new_cols = set(new_df.columns)

        return {
            "added_columns": list(new_cols - old_cols),
            "removed_columns": list(old_cols - new_cols),
            "common_columns": list(old_cols & new_cols),
            "old_row_count": len(old_df),
            "new_row_count": len(new_df),
            "row_diff": len(new_df) - len(old_df)
        }
