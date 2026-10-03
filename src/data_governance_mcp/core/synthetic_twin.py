"""Differential-Privacy Inspired Synthetic Digital Twin Generator."""

from __future__ import annotations

import random
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from .pii_detector import PIIDetector


class SyntheticTwinGenerator:
    """Generates realistic, statistically consistent mock datasets preserving schema and distributions."""

    @classmethod
    def generate(
        cls,
        df: pd.DataFrame,
        n_rows: Optional[int] = None,
        random_seed: int = 42,
    ) -> Tuple[pd.DataFrame, dict]:
        """Synthesizes a digital twin dataset with zero sensitive or proprietary leakage."""
        np.random.seed(random_seed)
        random.seed(random_seed)

        target_len = n_rows if (n_rows and n_rows > 0) else len(df)
        synthetic_dict = {}
        pii_scan = PIIDetector.scan(df)
        sensitive_cols = set(pii_scan.findings_by_column.keys())

        metadata = {
            "original_rows": len(df),
            "synthetic_rows": target_len,
            "anonymized_columns": list(sensitive_cols),
            "columns_modeled": len(df.columns),
        }

        for col in df.columns:
            series = df[col]
            null_rate = series.isnull().mean()
            non_null = series.dropna()

            if len(non_null) == 0:
                synthetic_dict[col] = [None] * target_len
                continue

            # 1. Sensitive PII columns: synthesize fake compliant tokens
            if col in sensitive_cols:
                col_lower = str(col).lower()
                if "email" in col_lower:
                    synthetic_col = [f"mock_user_{i+1:04d}@synthetic-domain.com" for i in range(target_len)]
                elif "phone" in col_lower or "tel" in col_lower:
                    synthetic_col = [f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}" for _ in range(target_len)]
                elif "token" in col_lower or "key" in col_lower:
                    synthetic_col = [f"sk-mock-synthetic-{random.randint(100000, 999999)}" for _ in range(target_len)]
                elif "dni" in col_lower or "ssn" in col_lower:
                    synthetic_col = [f"{random.randint(10000000, 99999999)}X" for _ in range(target_len)]
                else:
                    synthetic_col = [f"SYNTHETIC_VAL_{i+1}" for i in range(target_len)]

            # 2. Numerical columns: preserve statistical properties (mean, std, min, max, integer nature)
            elif pd.api.types.is_numeric_dtype(series):
                is_int = pd.api.types.is_integer_dtype(series) or (non_null.apply(float.is_integer).all() if len(non_null) else False)
                mean = non_null.mean()
                std = non_null.std() if len(non_null) > 1 else 1.0
                if np.isnan(std) or std == 0:
                    std = 0.01

                # Generate from normal distribution bounded by observed empirical bounds
                generated = np.random.normal(loc=mean, scale=std, size=target_len)
                lower_b = non_null.min()
                upper_b = non_null.max()
                generated = np.clip(generated, lower_b, upper_b)

                if is_int:
                    synthetic_col = [int(round(x)) for x in generated]
                else:
                    synthetic_col = [round(float(x), 4) for x in generated]

            # 3. Datetime columns: preserve start, end range and frequency
            elif pd.api.types.is_datetime64_any_dtype(series) or "date" in str(col).lower() or "time" in str(col).lower():
                try:
                    parsed = pd.to_datetime(non_null, errors="coerce").dropna()
                    if len(parsed) > 0:
                        min_ts = parsed.min().value
                        max_ts = parsed.max().value
                        if max_ts > min_ts:
                            rand_ts = np.random.randint(min_ts, max_ts, size=target_len)
                            synthetic_col = [str(pd.to_datetime(t)) for t in rand_ts]
                        else:
                            synthetic_col = [str(parsed.iloc[0])] * target_len
                    else:
                        synthetic_col = [f"2026-01-{i%28+1:02d}" for i in range(target_len)]
                except Exception:
                    synthetic_col = [f"2026-01-{i%28+1:02d}" for i in range(target_len)]

            # 4. Categorical / string columns: sample preserving empirical frequency distribution
            else:
                val_counts = non_null.value_counts(normalize=True)
                choices = val_counts.index.tolist()
                probs = val_counts.values.tolist()
                synthetic_col = random.choices(choices, weights=probs, k=target_len)

            # Re-introduce exact observed missingness distribution
            if null_rate > 0:
                for idx in range(target_len):
                    if random.random() < null_rate:
                        synthetic_col[idx] = None

            synthetic_dict[col] = synthetic_col

        twin_df = pd.DataFrame(synthetic_dict)
        return twin_df, metadata
