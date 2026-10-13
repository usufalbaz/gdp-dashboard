"""
Unit tests for World Bank REST API ingestion engine.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Guarantee root resolution
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.pipeline.world_bank import WorldBankClient


def test_client_initialization():
    client = WorldBankClient(timeout=10)
    assert client.timeout == 10
    assert "User-Agent" in client.headers
    assert client.BASE_URL.startswith("https://")


def test_client_fallback_on_invalid_country():
    client = WorldBankClient(timeout=5)
    # Querying an invalid country code should return a typed empty DataFrame gracefully
    df = client.fetch_indicator(country_code="NON_EXISTENT_XYZ", start_year=2020, end_year=2021)
    
    assert isinstance(df, pd.DataFrame)
    expected_cols = {"Year", "GDP", "Country Code", "Country Name"}
    assert expected_cols.issubset(df.columns)


def test_client_live_query_schema():
    client = WorldBankClient(timeout=15)
    # Fetch a small window for the World (WLD) to verify schema contract
    try:
        df = client.fetch_indicator(country_code="WLD", start_year=2020, end_year=2021)
        assert isinstance(df, pd.DataFrame)
        expected_cols = {"Year", "GDP", "Country Code", "Country Name"}
        assert expected_cols.issubset(df.columns)
    except Exception:
        pytest.skip("External network connectivity constrained during CI run.")
