"""Command-line interface for Data Governance MCP Server."""

from __future__ import annotations

import argparse
import sys
from .core.loader import DatasetLoader
from .core.dimensions import DataQualityEvaluator
from .core.pii_detector import PIIDetector
from .core.reporter import GovernanceReporter
from .server import run_server

# Ensure UTF-8 output across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="data-governance-mcp",
        description="Enterprise DAMA-DMBOK Data Quality & Governance MCP Server",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: run (Start MCP stdio server)
    run_parser = subparsers.add_parser("run", help="Start the MCP Server on stdio transport")

    # Command: audit (Run direct CLI audit)
    audit_parser = subparsers.add_parser("audit", help="Audit a dataset directly and print the markdown report")
    audit_parser.add_argument("file_path", help="Path to CSV, Parquet, JSON, or SQLite database")
    audit_parser.add_argument("--max-rows", type=int, default=50000, help="Maximum rows to inspect (default: 50,000)")
    audit_parser.add_argument("--json", action="store_true", help="Output audit report as structured JSON")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        if args.command is None and len(sys.argv) > 1:
            parser.print_help()
            sys.exit(1)
        # Default action is running MCP server
        run_server()

    elif args.command == "audit":
        try:
            df, source_desc = DatasetLoader.load(args.file_path, max_rows=args.max_rows)
            evaluator = DataQualityEvaluator(df, source_name=source_desc)
            scorecard = evaluator.evaluate_all()
            pii_result = PIIDetector.scan(df)

            if args.json:
                import json
                print(json.dumps(GovernanceReporter.render_json(scorecard, pii_result), indent=2))
            else:
                print(GovernanceReporter.render_markdown(scorecard, pii_result))
        except Exception as exc:
            print(f"Error during audit: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
