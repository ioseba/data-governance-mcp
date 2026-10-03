"""Unit tests for dataset loading functionality."""

import sqlite3
import pandas as pd
import pytest
from data_governance_mcp.core.loader import DatasetLoader


def test_load_inline_csv():
    raw_csv = "id,value\n1,100\n2,200\n"
    df, desc = DatasetLoader.load(raw_csv)
    assert len(df) == 2
    assert "Inline" in desc
    assert list(df.columns) == ["id", "value"]


def test_load_sqlite(tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE metrics (metric_name TEXT, val REAL);")
    cursor.execute("INSERT INTO metrics VALUES ('cpu', 45.2), ('mem', 78.1);")
    conn.commit()
    conn.close()

    df, desc = DatasetLoader.load(str(db_file))
    assert len(df) == 2
    assert "metrics" in desc
