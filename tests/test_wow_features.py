"""Unit tests for synthetic twin, token compressor, dbt exporter, and dashboard."""

import json
from pathlib import Path
import pandas as pd
from data_governance_mcp.core.synthetic_twin import SyntheticTwinGenerator
from data_governance_mcp.core.token_compressor import TokenCompressor
from data_governance_mcp.core.dbt_exporter import DbtExporter
from data_governance_mcp.core.dashboard import DashboardExporter
from data_governance_mcp.core.dimensions import DataQualityEvaluator
from data_governance_mcp.core.pii_detector import PIIDetector


def test_synthetic_twin_generator():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "email": ["alice@company.com", "bob@company.com", "charlie@company.com", None, "david@company.com"],
        "temp": [850.0, 852.1, 849.5, 851.0, 853.2],
        "status": ["OK", "OK", "WARN", "OK", "OK"],
    })
    twin, meta = SyntheticTwinGenerator.generate(df, n_rows=10)
    assert len(twin) == 10
    assert "email" in meta["anonymized_columns"]
    # Verify emails are replaced with synthetic mock addresses
    non_null_emails = twin["email"].dropna().tolist()
    assert all("synthetic-domain.com" in e for e in non_null_emails)
    # Verify temp values stay in realistic bounds
    assert twin["temp"].min() >= 840.0
    assert twin["temp"].max() <= 860.0


def test_token_compressor():
    df = pd.DataFrame({
        "timestamp": [f"2026-01-{i+1:02d}" for i in range(50)],
        "val_a": [float(i * 1.5) for i in range(50)],
        "val_b": [float(i * 3.0) for i in range(50)],
        "category": [f"CAT_{i % 3}" for i in range(50)],
    })
    res = TokenCompressor.compress(df, "test_dataset")
    assert res["metrics"]["original_tokens"] > res["metrics"]["compressed_tokens"]
    assert "val_a" in res["compressed_fingerprint"]
    assert "dimensions" in res["compressed_fingerprint"]


def test_dbt_exporter():
    df = pd.DataFrame({
        "id": [101, 102, 103],
        "category": ["A", "B", "A"],
        "cost": [10.5, 20.0, 15.2],
    })
    yml = DbtExporter.generate_dbt_schema_yml(df, model_name="stg_orders")
    assert "name: stg_orders" in yml
    assert "not_null" in yml
    assert "unique" in yml
    assert "accepted_values" in yml


def test_dashboard_exporter():
    df = pd.DataFrame({"sensor": [1, 2, 3], "reading": [10.0, 11.2, 10.5]})
    scorecard = DataQualityEvaluator(df, "sensor_data").evaluate_all()
    pii = PIIDetector.scan(df)
    html = DashboardExporter.generate_html(scorecard, pii)
    assert "<!DOCTYPE html>" in html
    assert "Data Governance & Quality Audit" in html
    assert "DAMA-DMBOK" in html
