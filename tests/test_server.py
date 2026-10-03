"""Unit tests for FastMCP server tools."""

import json
from pathlib import Path
from data_governance_mcp.server import audit_dataset, profile_schema, detect_pii, evaluate_dama_dimensions, suggest_remediations

SAMPLE_CSV = str(Path(__file__).parent.parent / "examples" / "sample_datasets" / "industrial_furnace_telemetry.csv")


def test_audit_dataset_tool():
    report = audit_dataset(SAMPLE_CSV)
    assert "# 🛡️ Data Governance & Quality Audit Report" in report
    assert "DAMA Overall Quality Index" in report


def test_profile_schema_tool():
    res_str = profile_schema(SAMPLE_CSV)
    data = json.loads(res_str)
    assert "columns" in data
    assert "furnace_id" in data["columns"]


def test_detect_pii_tool():
    res_str = detect_pii(SAMPLE_CSV)
    data = json.loads(res_str)
    assert data["has_pii_risk"] is True
    assert "operator_email" in data["findings_by_column"]


def test_evaluate_dama_dimensions_tool():
    res_str = evaluate_dama_dimensions(SAMPLE_CSV)
    data = json.loads(res_str)
    assert "overall_score" in data
    assert "Completeness" in data["dimensions"]


def test_suggest_remediations_tool():
    rem_str = suggest_remediations(SAMPLE_CSV)
    assert "Recommended Remediation Scripts" in rem_str
    assert "drop_duplicates" in rem_str
