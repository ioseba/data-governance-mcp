"""FastMCP Server implementation for Data Governance & Quality Audit."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP

from .core.loader import DatasetLoader
from .core.dimensions import DataQualityEvaluator
from .core.pii_detector import PIIDetector
from .core.reporter import GovernanceReporter

# Initialize FastMCP Server
mcp = FastMCP(
    name="Data Governance MCP",
    instructions="Enterprise-grade DAMA-DMBOK data quality audit and PII compliance server for AI agents.",
)


@mcp.tool()
def audit_dataset(
    file_path: str,
    max_rows: Optional[int] = 50000,
) -> str:
    """Performs an end-to-end DAMA-DMBOK quality audit and PII vulnerability scan on a dataset.

    Args:
        file_path: Absolute or relative path to CSV, Parquet, JSON, or SQLite database.
        max_rows: Maximum records to ingest for audit (default: 50,000).

    Returns:
        A formatted, executive-ready Markdown governance and compliance report.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path, max_rows=max_rows)
        evaluator = DataQualityEvaluator(df, source_name=source_desc)
        scorecard = evaluator.evaluate_all()
        pii_result = PIIDetector.scan(df)
        return GovernanceReporter.render_markdown(scorecard, pii_result)
    except Exception as exc:
        return f"Error auditing dataset '{file_path}': {str(exc)}"


@mcp.tool()
def profile_schema(file_path: str, max_rows: Optional[int] = 10000) -> str:
    """Profiles the dataset schema, data types, null rates, and distribution summaries.

    Args:
        file_path: Path to dataset file.
        max_rows: Maximum records to inspect.

    Returns:
        JSON string describing the tabular schema profile.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path, max_rows=max_rows)
        profile = {
            "source": source_desc,
            "rows_inspected": len(df),
            "columns_count": len(df.columns),
            "columns": {},
        }
        for col in df.columns:
            s = df[col]
            profile["columns"][str(col)] = {
                "dtype": str(s.dtype),
                "null_count": int(s.isnull().sum()),
                "null_percentage": round(float(s.isnull().mean()) * 100, 2),
                "unique_values": int(s.nunique()),
                "sample_values": s.dropna().astype(str).head(3).tolist(),
            }
        return json.dumps(profile, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def detect_pii(file_path: str, max_sample_rows: Optional[int] = 500) -> str:
    """Scans dataset for personally identifiable information (PII), secrets, and compliance liabilities.

    Args:
        file_path: Path to dataset file.
        max_sample_rows: Number of sample records to inspect (default: 500).

    Returns:
        JSON string containing PII findings, risk levels, and leakage warnings.
    """
    try:
        df, _ = DatasetLoader.load(file_path, max_rows=max_sample_rows)
        res = PIIDetector.scan(df, max_sample_rows=max_sample_rows or 500)
        return json.dumps(res.to_dict(), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def evaluate_dama_dimensions(file_path: str) -> str:
    """Evaluates dataset against the 6 core DAMA dimensions: Completeness, Uniqueness, Validity, Accuracy, Consistency, Timeliness.

    Args:
        file_path: Path to dataset file.

    Returns:
        JSON string with granular scores and diagnostics per dimension.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path)
        evaluator = DataQualityEvaluator(df, source_name=source_desc)
        scorecard = evaluator.evaluate_all()
        return json.dumps(scorecard.to_dict(), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def suggest_remediations(file_path: str) -> str:
    """Generates ready-to-run Python and SQL remediation code snippets to fix detected data flaws.

    Args:
        file_path: Path to dataset file.

    Returns:
        Markdown with concrete data cleaning snippets tailored to the dataset.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path)
        evaluator = DataQualityEvaluator(df, source_name=source_desc)
        scorecard = evaluator.evaluate_all()
        pii = PIIDetector.scan(df)

        lines = [f"# 🛠️ Recommended Remediation Scripts for `{source_desc}`\n"]

        # Duplicates
        dup_cnt = scorecard.dimension_scores["Uniqueness"].details.get("duplicate_rows", 0)
        if dup_cnt > 0:
            lines.append("### 1. Deduplication")
            lines.append("```python")
            lines.append("# Drop exact duplicate records")
            lines.append("df = df.drop_duplicates()")
            lines.append("```\n")

        # Missing values
        high_nulls = scorecard.dimension_scores["Completeness"].details.get("high_null_columns", {})
        if high_nulls:
            lines.append("### 2. Missing Value Imputation")
            lines.append("```python")
            for c in high_nulls:
                lines.append(f"# Column '{c}' has {high_nulls[c]} missing values")
                lines.append(f"df['{c}'] = df['{c}'].fillna(df['{c}'].median() if pd.api.types.is_numeric_dtype(df['{c}']) else 'UNKNOWN')")
            lines.append("```\n")

        # PII Masking
        if pii.has_pii_risk:
            lines.append("### 3. PII Tokenization / Masking")
            lines.append("```python")
            lines.append("import hashlib")
            for col in pii.findings_by_column:
                lines.append(f"# Mask sensitive column '{col}'")
                lines.append(f"df['{col}'] = df['{col}'].astype(str).apply(lambda x: hashlib.sha256(x.encode()).hexdigest()[:12])")
            lines.append("```\n")

        if len(lines) == 1:
            lines.append("✅ Dataset is already high quality! No immediate critical remediation scripts required.")

        return "\n".join(lines)
    except Exception as exc:
        return f"Error generating remediations: {str(exc)}"


def run_server():
    """Runs the MCP server via standard stdio transport."""
    mcp.run()


if __name__ == "__main__":
    run_server()
