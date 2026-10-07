import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from streamlit_app import calculate_cagr, load_and_transform_gdp_data

def test_calculate_cagr_standard():
    start_val = 100.0
    end_val = 200.0
    years = 10
    # Expected CAGR ~ 7.18%
    cagr = calculate_cagr(start_val, end_val, years)
    assert pytest.approx(cagr, 0.001) == 0.07177

def test_calculate_cagr_invalid():
    assert np.isnan(calculate_cagr(0, 100, 5))
    assert np.isnan(calculate_cagr(-50, 100, 5))
    assert np.isnan(calculate_cagr(100, 200, 0))

def test_load_and_transform_gdp_data():
    sample_file = Path(__file__).parent.parent / 'data/gdp_data.csv'
    if sample_file.exists():
        df = load_and_transform_gdp_data(sample_file)
        assert 'Country Name' in df.columns
        assert 'Year' in df.columns
        assert 'GDP' in df.columns
        assert df['Year'].dtype in [np.int64, int, float]
