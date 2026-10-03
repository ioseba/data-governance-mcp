"""Dataset loader supporting CSV, Parquet, JSON, and SQLite sources."""

from __future__ import annotations

import io
import os
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


class DatasetLoader:
    """Robust dataset ingestion helper for local and embedded data."""

    @staticmethod
    def load(
        source: str,
        table_name: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, str]:
        """Loads data from a file path, SQLite URI, or raw delimited string.

        Returns:
            Tuple[pd.DataFrame, str]: Loaded DataFrame and resolved description.
        """
        source_str = source.strip()

        # Handle raw inline CSV content if not an existing path
        if "\n" in source_str and not os.path.exists(source_str):
            try:
                df = pd.read_csv(io.StringIO(source_str), nrows=max_rows)
                return df, "Inline CSV snippet"
            except Exception as exc:
                raise ValueError(f"Failed to parse inline CSV: {exc}") from exc

        path = Path(source_str)

        # Check SQLite URI format: "path/to/db.sqlite::table_name"
        if "::" in source_str:
            db_path_str, tbl = source_str.split("::", 1)
            db_path = Path(db_path_str)
            if not db_path.exists():
                raise FileNotFoundError(f"SQLite file not found: {db_path}")
            conn = sqlite3.connect(db_path)
            query = f"SELECT * FROM {tbl}"
            if max_rows:
                query += f" LIMIT {max_rows}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, f"SQLite ({db_path.name} -> {tbl})"

        if not path.exists():
            raise FileNotFoundError(f"File not found: {source_str}")

        suffix = path.suffix.lower()

        if suffix in (".csv", ".tsv", ".txt"):
            # Robust delimiter sniffing
            try:
                df = pd.read_csv(path, sep=None, engine="python", nrows=max_rows)
            except Exception:
                df = pd.read_csv(path, sep=",", nrows=max_rows)
            return df, f"Delimited file ({path.name})"

        if suffix in (".parquet", ".pq"):
            df = pd.read_parquet(path)
            if max_rows and len(df) > max_rows:
                df = df.iloc[:max_rows]
            return df, f"Parquet file ({path.name})"

        if suffix in (".json", ".jsonl"):
            try:
                df = pd.read_json(path, lines=suffix == ".jsonl")
            except ValueError:
                df = pd.read_json(path)
            if max_rows and len(df) > max_rows:
                df = df.iloc[:max_rows]
            return df, f"JSON file ({path.name})"

        if suffix in (".sqlite", ".db", ".sqlite3"):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
            if not tables:
                conn.close()
                raise ValueError(f"No user tables found in SQLite database {path.name}")
            selected_table = table_name if (table_name and table_name in tables) else tables[0]
            query = f"SELECT * FROM {selected_table}"
            if max_rows:
                query += f" LIMIT {max_rows}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, f"SQLite ({path.name} -> {selected_table})"

        # Fallback to standard CSV
        df = pd.read_csv(path, nrows=max_rows)
        return df, f"Dataset ({path.name})"
