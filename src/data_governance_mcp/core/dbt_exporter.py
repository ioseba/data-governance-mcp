"""Automated dbt and Data Quality Test Suite Exporter."""

from __future__ import annotations

import pandas as pd
from .dimensions import QualityScorecard


class DbtExporter:
    """Translates DAMA audit discoveries into production-grade dbt schema.yml tests."""

    @classmethod
    def generate_dbt_schema_yml(
        cls,
        df: pd.DataFrame,
        model_name: str = "stg_dataset",
        scorecard: QualityScorecard = None,
    ) -> str:
        lines = [
            "version: 2",
            "",
            "models:",
            f"  - name: {model_name}",
            f"    description: 'Auto-generated DAMA-compliant data model for {model_name}.'",
            "    columns:",
        ]

        for col in df.columns:
            series = df[col]
            null_rate = series.isnull().mean()
            nunique = series.nunique()
            is_numeric = pd.api.types.is_numeric_dtype(series)

            tests = []

            # 1. Not null rule (if column has 0 or negligible nulls)
            if null_rate == 0:
                tests.append("not_null")

            # 2. Unique rule (candidate key)
            if nunique == len(df) and len(df) > 0 and null_rate == 0:
                tests.append("unique")

            # 3. Categorical accepted_values (if low cardinality: <= 5 unique values and non-numeric)
            if not is_numeric and 1 < nunique <= 5:
                vals = [str(v) for v in series.dropna().unique().tolist()]
                vals_formatted = ", ".join([f"'{v}'" for v in vals])
                tests.append(f"accepted_values:\n              values: [{vals_formatted}]")

            # 4. Numeric range constraints if positive/physical
            if is_numeric and len(series.dropna()) > 0:
                min_v = series.min()
                if min_v >= 0:
                    tests.append(f"dbt_utils.expression_is_true:\n              expression: '>= 0'")

            lines.append(f"      - name: {col}")
            lines.append(f"        description: 'Column {col} (dtype: {series.dtype}).'")
            if tests:
                lines.append("        tests:")
                for t in tests:
                    if "\n" in t:
                        lines.append(f"          - {t}")
                    else:
                        lines.append(f"          - {t}")
            else:
                lines.append("        # No baseline strict constraints flagged")

        return "\n".join(lines)
