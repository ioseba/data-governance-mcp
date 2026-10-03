"""Command-line interface for Data Governance MCP Server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .core.loader import DatasetLoader
from .core.dimensions import DataQualityEvaluator
from .core.pii_detector import PIIDetector
from .core.reporter import GovernanceReporter
from .core.synthetic_twin import SyntheticTwinGenerator
from .core.token_compressor import TokenCompressor
from .core.dbt_exporter import DbtExporter
from .core.dashboard import DashboardExporter
from .server import run_server

# Ensure UTF-8 output across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="data-governance-mcp",
        description="Data Governance MCP: Autonomous DAMA Quality, Privacy Twin & Token Optimizer for AI Coding",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: run
    subparsers.add_parser("run", help="Start the MCP Server on stdio transport")

    # Command: audit
    p_audit = subparsers.add_parser("audit", help="Audit dataset against DAMA dimensions & scan PII")
    p_audit.add_argument("file_path", help="Path to CSV, Parquet, JSON, or SQLite database")
    p_audit.add_argument("--max-rows", type=int, default=50000, help="Maximum rows to inspect (default: 50,000)")
    p_audit.add_argument("--json", action="store_true", help="Output audit report as structured JSON")

    # Command: twin
    p_twin = subparsers.add_parser("twin", help="Generate a privacy-safe synthetic digital twin")
    p_twin.add_argument("file_path", help="Path to input dataset")
    p_twin.add_argument("--out", default="synthetic_twin.csv", help="Output CSV path (default: synthetic_twin.csv)")
    p_twin.add_argument("--rows", type=int, default=None, help="Number of synthetic rows to generate")

    # Command: compress
    p_comp = subparsers.add_parser("compress", help="Compress dataset context to save 90-95% LLM tokens")
    p_comp.add_argument("file_path", help="Path to input dataset")

    # Command: dbt
    p_dbt = subparsers.add_parser("dbt", help="Generate production-ready dbt schema.yml tests")
    p_dbt.add_argument("file_path", help="Path to input dataset")
    p_dbt.add_argument("--model", default="stg_dataset", help="Target dbt model name")

    # Command: dashboard
    p_dash = subparsers.add_parser("dashboard", help="Export standalone interactive HTML executive report")
    p_dash.add_argument("file_path", help="Path to input dataset")
    p_dash.add_argument("--out", default="governance_dashboard.html", help="Output HTML file path")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        if args.command is None and len(sys.argv) > 1:
            parser.print_help()
            sys.exit(1)
        run_server()

    elif args.command == "audit":
        df, source_desc = DatasetLoader.load(args.file_path, max_rows=args.max_rows)
        scorecard = DataQualityEvaluator(df, source_name=source_desc).evaluate_all()
        pii_result = PIIDetector.scan(df)
        if args.json:
            print(json.dumps(GovernanceReporter.render_json(scorecard, pii_result), indent=2))
        else:
            print(GovernanceReporter.render_markdown(scorecard, pii_result))

    elif args.command == "twin":
        df, _ = DatasetLoader.load(args.file_path)
        twin_df, meta = SyntheticTwinGenerator.generate(df, n_rows=args.rows)
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        twin_df.to_csv(out_p, index=False)
        print(f"Generated synthetic digital twin: {out_p.resolve()} ({len(twin_df)} rows)")
        print(f"Anonymized sensitive columns: {meta['anonymized_columns']}")

    elif args.command == "compress":
        df, source_desc = DatasetLoader.load(args.file_path)
        res = TokenCompressor.compress(df, dataset_name=source_desc)
        print(f"# Token Optimization Report for {source_desc}")
        print(f"- Raw Input Tokens: ~{res['metrics']['original_tokens']:,}")
        print(f"- Compressed Tokens: ~{res['metrics']['compressed_tokens']:,}")
        print(f"- Token Reduction: {res['metrics']['compression_ratio']}")
        print(f"- Savings per LLM turn: {res['metrics']['estimated_savings_per_call']}\n")
        print("```json\n" + res["compressed_fingerprint"] + "\n```")

    elif args.command == "dbt":
        df, _ = DatasetLoader.load(args.file_path)
        print(DbtExporter.generate_dbt_schema_yml(df, model_name=args.model))

    elif args.command == "dashboard":
        df, source_desc = DatasetLoader.load(args.file_path)
        scorecard = DataQualityEvaluator(df, source_name=source_desc).evaluate_all()
        pii = PIIDetector.scan(df)
        html_code = DashboardExporter.generate_html(scorecard, pii)
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(html_code, encoding="utf-8")
        print(f"Generated standalone HTML dashboard: {out_p.resolve()}")


if __name__ == "__main__":
    main()
