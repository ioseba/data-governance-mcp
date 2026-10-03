"""Unit tests for PII detection engine."""

import pandas as pd
from data_governance_mcp.core.pii_detector import PIIDetector


def test_pii_detection_clean():
    df = pd.DataFrame({"sensor_reading": [20.5, 21.0, 19.8], "unit": ["C", "C", "C"]})
    res = PIIDetector.scan(df)
    assert not res.has_pii_risk
    assert res.risk_level == "NONE"
    assert res.total_findings == 0


def test_pii_detection_email_and_secrets():
    df = pd.DataFrame({
        "username": ["admin", "dev"],
        "contact": ["user1@company.org", "engineer@test.com"],
        "api_key": ["sk-123456789012345678901234", "clean_val"],
    })
    res = PIIDetector.scan(df)
    assert res.has_pii_risk
    assert res.risk_level in ("HIGH", "CRITICAL")
    assert "contact" in res.findings_by_column
    assert "api_key" in res.findings_by_column
