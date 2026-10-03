"""PII and Sensitive Information Detector for Enterprise Data Governance."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List
import pandas as pd


@dataclass
class PIIScanResult:
    """Findings from scanning dataset columns for sensitive data and leakage risks."""
    total_findings: int
    has_pii_risk: bool
    risk_level: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    findings_by_column: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    leakage_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_findings": self.total_findings,
            "has_pii_risk": self.has_pii_risk,
            "risk_level": self.risk_level,
            "findings_by_column": self.findings_by_column,
            "leakage_warnings": self.leakage_warnings,
        }


class PIIDetector:
    """Scans tabular records and schema column names for privacy & compliance liabilities."""

    PATTERNS = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
        "PHONE": re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "IPV4": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
        "SPANISH_DNI_NIE": re.compile(r"\b(?:[XYZ]?\d{7,8}[A-Z]|\d{8}[A-Z])\b", re.IGNORECASE),
        "API_SECRET_TOKEN": re.compile(r"\b(?:sk-[A-Za-z0-9]{20,48}|ghp_[A-Za-z0-9]{36}|Bearer\s+[A-Za-z0-9\-_]{20,})\b"),
    }

    SENSITIVE_COLUMN_KEYWORDS = {
        "CRITICAL": ["password", "passwd", "secret", "token", "api_key", "private_key", "ssn", "dni", "tarjeta", "credit_card"],
        "HIGH": ["email", "phone", "telefono", "salary", "salario", "sueldo", "iban", "cuenta_bancaria", "dob", "birthdate"],
        "MEDIUM": ["address", "direccion", "ip_address", "full_name", "first_name", "last_name", "apellidos"],
    }

    @classmethod
    def scan(cls, df: pd.DataFrame, max_sample_rows: int = 500) -> PIIScanResult:
        findings_by_col: Dict[str, List[Dict[str, Any]]] = {}
        total_findings = 0
        warnings: List[str] = []
        max_severity_rank = 0  # 0: None, 1: Low, 2: Medium, 3: High, 4: Critical

        sample_df = df.iloc[:max_sample_rows] if len(df) > max_sample_rows else df

        for col in df.columns:
            col_findings = []
            col_lower = str(col).lower().replace(" ", "_").replace("-", "_")

            # 1. Header heuristics
            for severity, keywords in cls.SENSITIVE_COLUMN_KEYWORDS.items():
                for kw in keywords:
                    if kw in col_lower:
                        rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2}[severity]
                        max_severity_rank = max(max_severity_rank, rank)
                        finding = {
                            "type": "HEADER_RISK",
                            "severity": severity,
                            "detail": f"Column name matches sensitive keyword '{kw}'.",
                        }
                        col_findings.append(finding)
                        total_findings += 1
                        break

            # 2. Content pattern matching on string/object columns
            if pd.api.types.is_string_dtype(sample_df[col]) or pd.api.types.is_object_dtype(sample_df[col]):
                s = sample_df[col].dropna().astype(str)
                if len(s) > 0:
                    for pii_name, pattern in cls.PATTERNS.items():
                        matches = s.apply(lambda val: bool(pattern.search(val)))
                        match_count = int(matches.sum())
                        if match_count > 0:
                            severity = "CRITICAL" if pii_name in ("API_SECRET_TOKEN", "CREDIT_CARD") else "HIGH"
                            rank = 4 if severity == "CRITICAL" else 3
                            max_severity_rank = max(max_severity_rank, rank)
                            finding = {
                                "type": "PATTERN_MATCH",
                                "pattern": pii_name,
                                "severity": severity,
                                "sample_matches": match_count,
                                "sample_rate": round(match_count / len(s), 4),
                            }
                            col_findings.append(finding)
                            total_findings += 1

            if col_findings:
                findings_by_col[col] = col_findings

        rank_map = {0: "NONE", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
        overall_level = rank_map[max_severity_rank]

        if overall_level in ("HIGH", "CRITICAL"):
            warnings.append(
                f"Data contains high-risk PII/credentials ({overall_level}). Do NOT ingest into untrusted external LLM prompts without tokenization or hashing."
            )

        return PIIScanResult(
            total_findings=total_findings,
            has_pii_risk=total_findings > 0,
            risk_level=overall_level,
            findings_by_column=findings_by_col,
            leakage_warnings=warnings,
        )
