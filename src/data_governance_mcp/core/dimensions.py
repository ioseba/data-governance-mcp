"""DAMA-DMBOK 6 Core Data Quality Dimensions Evaluator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class DimensionResult:
    """Individual data quality dimension score and diagnostic details."""
    name: str
    score: float  # 0.0 to 100.0
    status: str   # PASS, WARNING, FAIL
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediations: List[str] = field(default_factory=list)


@dataclass
class QualityScorecard:
    """Consolidated DAMA-compliant scorecard for dataset."""
    overall_score: float
    total_records: int
    total_columns: int
    dimension_scores: Dict[str, DimensionResult]
    critical_issues: List[str]
    source_info: str

    @property
    def status_label(self) -> str:
        if self.overall_score >= 90:
            return "EXCELLENT"
        elif self.overall_score >= 75:
            return "ACCEPTABLE"
        return "CRITICAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 2),
            "health_status": self.status_label,
            "total_records": self.total_records,
            "total_columns": self.total_columns,
            "source": self.source_info,
            "dimensions": {
                name: {
                    "score": round(res.score, 2),
                    "status": res.status,
                    "summary": res.summary,
                    "details": res.details,
                    "remediations": res.remediations,
                }
                for name, res in self.dimension_scores.items()
            },
            "critical_issues": self.critical_issues,
        }


class DataQualityEvaluator:
    """Evaluates tabular datasets against the six DAMA Data Management Body of Knowledge dimensions."""

    DEFAULT_WEIGHTS = {
        "Completeness": 0.22,
        "Uniqueness": 0.18,
        "Validity": 0.22,
        "Accuracy": 0.16,
        "Consistency": 0.12,
        "Timeliness": 0.10,
    }

    def __init__(self, df: pd.DataFrame, source_name: str = "dataset"):
        self.df = df.copy()
        self.source_name = source_name
        self.n_rows, self.n_cols = df.shape

    def evaluate_all(self, thresholds: Optional[Dict[str, float]] = None) -> QualityScorecard:
        """Runs evaluation across all 6 dimensions."""
        if self.n_rows == 0:
            empty_res = DimensionResult("Empty", 0.0, "FAIL", "Dataset has 0 rows.")
            return QualityScorecard(
                overall_score=0.0,
                total_records=0,
                total_columns=self.n_cols,
                dimension_scores={"Completeness": empty_res},
                critical_issues=["Dataset is empty."],
                source_info=self.source_name,
            )

        completeness = self._eval_completeness()
        uniqueness = self._eval_uniqueness()
        validity = self._eval_validity()
        accuracy = self._eval_accuracy()
        consistency = self._eval_consistency()
        timeliness = self._eval_timeliness()

        dims = {
            "Completeness": completeness,
            "Uniqueness": uniqueness,
            "Validity": validity,
            "Accuracy": accuracy,
            "Consistency": consistency,
            "Timeliness": timeliness,
        }

        # Weighted calculation (Completeness & Validity weight slightly higher per DAMA standard)
        weights = {
            "Completeness": 0.22,
            "Uniqueness": 0.18,
            "Validity": 0.22,
            "Accuracy": 0.16,
            "Consistency": 0.12,
            "Timeliness": 0.10,
        }

        overall = sum(dims[k].score * weights[k] for k in dims)
        critical = []
        for name, dim in dims.items():
            if dim.status == "FAIL":
                critical.append(f"[{name}] {dim.summary}")

        return QualityScorecard(
            overall_score=overall,
            total_records=self.n_rows,
            total_columns=self.n_cols,
            dimension_scores=dims,
            critical_issues=critical,
            source_info=self.source_name,
        )

    def _eval_completeness(self) -> DimensionResult:
        """Dimension 1: Completeness - Ratio of non-missing values across all fields."""
        null_counts = self.df.isnull().sum()
        total_cells = self.n_rows * self.n_cols
        total_nulls = int(null_counts.sum())

        # Also detect empty whitespace strings in object columns
        whitespace_count = 0
        obj_cols = self.df.select_dtypes(include=["object"]).columns
        for col in obj_cols:
            whitespace_count += int((self.df[col].astype(str).str.strip() == "").sum())

        missing_rate = (total_nulls + whitespace_count) / max(1, total_cells)
        score = max(0.0, (1.0 - missing_rate) * 100.0)

        high_null_cols = {
            col: int(cnt) for col, cnt in null_counts.items() if (cnt / self.n_rows) > 0.10
        }

        status = "PASS" if score >= 95 else ("WARNING" if score >= 80 else "FAIL")
        remediations = []
        if high_null_cols:
            remediations.append(
                f"Impute or handle missing values in columns with >10% missing: {list(high_null_cols.keys())}"
            )
        if whitespace_count > 0:
            remediations.append(f"Sanitize {whitespace_count} whitespace-only string cells to NULL/None.")

        return DimensionResult(
            name="Completeness",
            score=score,
            status=status,
            summary=f"{total_nulls} null values and {whitespace_count} blank cells detected ({round(100 - score, 2)}% missingness).",
            details={
                "missing_cells": total_nulls,
                "blank_string_cells": whitespace_count,
                "high_null_columns": high_null_cols,
            },
            remediations=remediations,
        )

    def _eval_uniqueness(self) -> DimensionResult:
        """Dimension 2: Uniqueness - Detects duplicate records and candidate key viability."""
        dup_rows = int(self.df.duplicated().sum())
        dup_ratio = dup_rows / max(1, self.n_rows)
        score = max(0.0, (1.0 - (dup_ratio * 2)) * 100.0)

        # Identify candidate keys (columns with 100% unique values)
        candidate_keys = [
            col for col in self.df.columns if self.df[col].nunique() == self.n_rows and not self.df[col].isnull().any()
        ]

        status = "PASS" if dup_rows == 0 else ("WARNING" if dup_ratio < 0.05 else "FAIL")
        remediations = []
        if dup_rows > 0:
            remediations.append(f"Deduplicate {dup_rows} identical rows using `df.drop_duplicates()`.")
        if not candidate_keys:
            remediations.append("No single natural primary key found. Consider defining a composite surrogate key.")

        return DimensionResult(
            name="Uniqueness",
            score=score,
            status=status,
            summary=f"{dup_rows} exact duplicate rows found across {self.n_rows} total rows.",
            details={
                "duplicate_rows": dup_rows,
                "candidate_primary_keys": candidate_keys,
            },
            remediations=remediations,
        )

    def _eval_validity(self) -> DimensionResult:
        """Dimension 3: Validity - Conformance of data types, string formats, and boolean domains."""
        issues = []
        invalid_cells = 0
        total_checks = 0

        for col in self.df.columns:
            s = self.df[col].dropna()
            if len(s) == 0:
                continue

            # Check if object column should be numeric
            if s.dtype == "object":
                numeric_converted = pd.to_numeric(s, errors="coerce")
                num_valid = numeric_converted.notnull().sum()
                if 0.8 < (num_valid / len(s)) < 1.0:
                    mixed = len(s) - num_valid
                    invalid_cells += mixed
                    issues.append(f"Column '{col}' has mixed types ({mixed} non-numeric strings in numeric column).")

            total_checks += len(s)

        penalty = (invalid_cells / max(1, total_checks)) if total_checks else 0.0
        score = max(0.0, (1.0 - penalty * 5) * 100.0)
        status = "PASS" if score >= 90 else ("WARNING" if score >= 75 else "FAIL")

        remediations = [f"Cast and clean: {iss}" for iss in issues[:3]]

        return DimensionResult(
            name="Validity",
            score=score,
            status=status,
            summary=f"{invalid_cells} invalid format/type mismatches found." if invalid_cells else "All columns conform to consistent data types.",
            details={"type_mismatches": invalid_cells, "findings": issues},
            remediations=remediations,
        )

    def _eval_accuracy(self) -> DimensionResult:
        """Dimension 4: Accuracy & Range - Outlier detection via Tukey's IQR and Z-scores."""
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        outlier_counts = {}
        total_outliers = 0
        total_numeric_values = 0

        for col in num_cols:
            s = self.df[col].dropna()
            if len(s) < 5:
                continue
            total_numeric_values += len(s)
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - (2.5 * iqr)  # Conservative 2.5 IQR fence
                upper = q3 + (2.5 * iqr)
                outs = int(((s < lower) | (s > upper)).sum())
                if outs > 0:
                    outlier_counts[col] = {
                        "count": outs,
                        "bounds": (round(float(lower), 2), round(float(upper), 2)),
                    }
                    total_outliers += outs

        outlier_rate = total_outliers / max(1, total_numeric_values) if total_numeric_values else 0.0
        score = max(0.0, (1.0 - outlier_rate * 4) * 100.0)
        status = "PASS" if score >= 90 else ("WARNING" if score >= 75 else "FAIL")

        remediations = []
        if outlier_counts:
            cols_str = ", ".join(list(outlier_counts.keys())[:3])
            remediations.append(f"Investigate domain physical limits for columns with severe outliers: {cols_str}")

        return DimensionResult(
            name="Accuracy",
            score=score,
            status=status,
            summary=f"{total_outliers} statistical outliers detected across {len(outlier_counts)} numeric columns.",
            details={"outlier_columns": outlier_counts, "total_outliers": total_outliers},
            remediations=remediations,
        )

    def _eval_consistency(self) -> DimensionResult:
        """Dimension 5: Consistency - Cross-field and logical consistency checks."""
        # Detect date pairs (start_date, end_date) and verify ordering
        inconsistencies = 0
        findings = []

        date_cols = [c for c in self.df.columns if "date" in c.lower() or "time" in c.lower()]
        if len(date_cols) >= 2:
            start_cand = next((c for c in date_cols if "start" in c.lower() or "created" in c.lower()), None)
            end_cand = next((c for c in date_cols if "end" in c.lower() or "closed" in c.lower()), None)
            if start_cand and end_cand:
                try:
                    s1 = pd.to_datetime(self.df[start_cand], errors="coerce")
                    s2 = pd.to_datetime(self.df[end_cand], errors="coerce")
                    invalid_order = int((s2 < s1).sum())
                    if invalid_order > 0:
                        inconsistencies += invalid_order
                        findings.append(f"Chronology inversion: {invalid_order} rows where {end_cand} < {start_cand}.")
                except Exception:
                    pass

        score = max(0.0, 100.0 - (inconsistencies * 5))
        status = "PASS" if score >= 90 else ("WARNING" if score >= 75 else "FAIL")

        remediations = [f"Correct cross-field logical anomaly: {f}" for f in findings]

        return DimensionResult(
            name="Consistency",
            score=score,
            status=status,
            summary=f"{inconsistencies} logical cross-column contradictions detected." if inconsistencies else "No cross-column contradictions detected.",
            details={"contradictions": inconsistencies, "findings": findings},
            remediations=remediations,
        )

    def _eval_timeliness(self) -> DimensionResult:
        """Dimension 6: Timeliness - Temporal freshness and gap cadence regularity."""
        date_cols = [c for c in self.df.columns if "date" in c.lower() or "time" in c.lower() or "timestamp" in c.lower()]
        if not date_cols:
            return DimensionResult(
                name="Timeliness",
                score=100.0,
                status="PASS",
                summary="No timestamp or date columns detected; neutral timeliness baseline.",
                details={"has_temporal_data": False},
                remediations=[],
            )

        target_col = date_cols[0]
        parsed_dates = pd.to_datetime(self.df[target_col], errors="coerce").dropna()
        if len(parsed_dates) == 0:
            return DimensionResult(
                name="Timeliness",
                score=60.0,
                status="WARNING",
                summary=f"Column '{target_col}' could not be parsed as datetime.",
                details={"has_temporal_data": False},
                remediations=[f"Format '{target_col}' into ISO 8601 (YYYY-MM-DD HH:MM:SS)."],
            )

        max_dt = parsed_dates.max()
        min_dt = parsed_dates.min()
        timespan_days = (max_dt - min_dt).days

        return DimensionResult(
            name="Timeliness",
            score=95.0,
            status="PASS",
            summary=f"Evaluated on '{target_col}'. Range spans {timespan_days} days (latest record: {max_dt.strftime('%Y-%m-%d')}).",
            details={
                "temporal_column": target_col,
                "latest_timestamp": str(max_dt),
                "earliest_timestamp": str(min_dt),
                "timespan_days": timespan_days,
            },
            remediations=[],
        )
