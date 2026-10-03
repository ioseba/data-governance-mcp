"""Unit tests for DAMA-DMBOK 6 data quality dimensions."""

import pandas as pd
import pytest
from data_governance_mcp.core.dimensions import DataQualityEvaluator


def test_completeness_perfect():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    evaluator = DataQualityEvaluator(df, "clean_test")
    res = evaluator._eval_completeness()
    assert res.score == 100.0
    assert res.status == "PASS"


def test_completeness_with_nulls_and_blanks():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "   ", "z"]})
    evaluator = DataQualityEvaluator(df, "dirty_test")
    res = evaluator._eval_completeness()
    assert res.score < 100.0
    assert res.details["missing_cells"] == 1
    assert res.details["blank_string_cells"] == 1


def test_uniqueness_with_duplicates():
    df = pd.DataFrame({"id": [1, 1, 2], "val": ["a", "a", "b"]})
    evaluator = DataQualityEvaluator(df, "dup_test")
    res = evaluator._eval_uniqueness()
    assert res.details["duplicate_rows"] == 1
    assert res.score < 100.0


def test_accuracy_outliers():
    df = pd.DataFrame({"measurement": [10.0, 10.2, 10.1, 9.9, 10.3, 10.0, 999.0]})
    evaluator = DataQualityEvaluator(df, "outlier_test")
    res = evaluator._eval_accuracy()
    assert res.details["total_outliers"] >= 1
    assert "measurement" in res.details["outlier_columns"]


def test_consistency_chronology_inversion():
    df = pd.DataFrame({
        "start_date": ["2026-01-01", "2026-02-01"],
        "end_date": ["2026-01-10", "2026-01-15"],  # Second row has end_date < start_date
    })
    evaluator = DataQualityEvaluator(df, "timeline_test")
    res = evaluator._eval_consistency()
    assert res.details["contradictions"] == 1


def test_evaluate_all_summary():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "temp": [100.0, 101.5, 100.8],
        "sensor_id": ["S1", "S2", "S3"],
    })
    evaluator = DataQualityEvaluator(df, "healthy_test")
    scorecard = evaluator.evaluate_all()
    assert scorecard.overall_score >= 90.0
    assert len(scorecard.critical_issues) == 0
