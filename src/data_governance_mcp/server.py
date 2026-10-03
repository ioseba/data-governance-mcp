"""FastMCP Server implementation for Data Governance & Quality Audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP

from .core.loader import DatasetLoader
from .core.dimensions import DataQualityEvaluator
from .core.pii_detector import PIIDetector
from .core.reporter import GovernanceReporter
from .core.synthetic_twin import SyntheticTwinGenerator
from .core.token_compressor import TokenCompressor
from .core.dbt_exporter import DbtExporter
from .core.dashboard import DashboardExporter

# Initialize FastMCP Server
try:
    mcp = FastMCP(
        "Data Governance MCP",
        instructions="Enterprise-grade DAMA-DMBOK data quality audit, synthetic privacy digital twin, and token optimization server for AI agents.",
    )
except TypeError:
    mcp = FastMCP("Data Governance MCP")


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
def generate_synthetic_twin(
    file_path: str,
    output_csv_path: Optional[str] = None,
    n_rows: Optional[int] = None,
) -> str:
    """Generates a 100% privacy-safe synthetic digital twin of a dataset, preserving schema and statistical distributions.

    Enables safe vibe coding in Cursor/Claude without uploading proprietary or sensitive company records.

    Args:
        file_path: Path to real production dataset.
        output_csv_path: Optional path to save the generated synthetic CSV file.
        n_rows: Number of synthetic rows to generate (default: matches input dataset size).

    Returns:
        Summary of modeled columns, anonymized fields, and sample synthetic preview records.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path)
        twin_df, meta = SyntheticTwinGenerator.generate(df, n_rows=n_rows)

        if output_csv_path:
            out_p = Path(output_csv_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            twin_df.to_csv(out_p, index=False)
            meta["saved_to"] = str(out_p.resolve())

        preview = twin_df.head(3).to_dict(orient="records")
        return json.dumps({"status": "SUCCESS", "metadata": meta, "sample_preview": preview}, indent=2, default=str)
    except Exception as exc:
        return json.dumps({"status": "ERROR", "error": str(exc)})


@mcp.tool()
def compress_context_for_llm(file_path: str, max_rows: Optional[int] = 10000) -> str:
    """Compresses large tabular datasets by 90-95% into a dense statistical context fingerprint.

    Dramatically reduces token consumption and eliminates LLM context window overflows in Cursor / Claude.

    Args:
        file_path: Path to dataset file.
        max_rows: Maximum records to inspect for compression.

    Returns:
        Ultra-dense JSON fingerprint with schema, distributions, collinearity, and token savings metrics.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path, max_rows=max_rows)
        res = TokenCompressor.compress(df, dataset_name=source_desc)
        return json.dumps(res, indent=2, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def export_dbt_tests(file_path: str, model_name: str = "stg_dataset") -> str:
    """Automatically translates DAMA quality findings into production-ready dbt schema.yml tests.

    Args:
        file_path: Path to dataset file.
        model_name: Target dbt model name.

    Returns:
        Ready-to-commit dbt schema.yml content with not_null, unique, and accepted_values tests.
    """
    try:
        df, _ = DatasetLoader.load(file_path)
        return DbtExporter.generate_dbt_schema_yml(df, model_name=model_name)
    except Exception as exc:
        return f"# Error generating dbt tests: {str(exc)}"


@mcp.tool()
def export_html_dashboard(
    file_path: str,
    output_html_path: str = "governance_dashboard.html",
) -> str:
    """Exports a self-contained, interactive executive HTML audit dashboard with zero external dependencies.

    Args:
        file_path: Path to dataset file.
        output_html_path: Destination path for HTML file.

    Returns:
        Confirmation message with path to open in browser.
    """
    try:
        df, source_desc = DatasetLoader.load(file_path)
        evaluator = DataQualityEvaluator(df, source_name=source_desc)
        scorecard = evaluator.evaluate_all()
        pii = PIIDetector.scan(df)
        html_content = DashboardExporter.generate_html(scorecard, pii)

        out_p = Path(output_html_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(html_content, encoding="utf-8")
        return f"Successfully generated interactive dashboard: {out_p.resolve()}"
    except Exception as exc:
        return f"Error exporting HTML dashboard: {str(exc)}"


@mcp.tool()
def profile_schema(file_path: str, max_rows: Optional[int] = 10000) -> str:
    """Profiles the dataset schema, data types, null rates, and distribution summaries."""
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
    """Scans dataset for personally identifiable information (PII), secrets, and compliance liabilities."""
    try:
        df, _ = DatasetLoader.load(file_path, max_rows=max_sample_rows)
        res = PIIDetector.scan(df, max_sample_rows=max_sample_rows or 500)
        return json.dumps(res.to_dict(), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def evaluate_dama_dimensions(file_path: str) -> str:
    """Evaluates dataset against the 6 core DAMA dimensions: Completeness, Uniqueness, Validity, Accuracy, Consistency, Timeliness."""
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

        lines = [f"# Recommended Remediation Scripts for `{source_desc}`\n"]

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
            lines.append("Dataset is already high quality! No immediate critical remediation scripts required.")

        return "\n".join(lines)
    except Exception as exc:
        return f"Error generating remediations: {str(exc)}"


def run_server():
    """Runs the MCP server via standard stdio transport."""
    mcp.run()


if __name__ == "__main__":
    run_server()
