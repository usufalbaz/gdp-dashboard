"""
Advanced Macroeconomic Analytics Engine.
Provides real-world crisis shock detection, global GDP share calculation,
and decade-by-decade performance profiling without synthetic extrapolations.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np


def detect_macro_crises(series: pd.Series, contraction_threshold: float = -3.0) -> pd.Series:
    """
    Identifies historical economic shocks, currency devaluations, and severe recessions.
    Flags years where Year-over-Year contraction drops beyond the threshold.
    """
    if series.empty:
        return pd.Series(dtype=bool)
    
    growth = series.pct_change() * 100.0
    return growth <= contraction_threshold


def calculate_global_share(country_gdp: float, world_gdp: float) -> float:
    """
    Computes the nation's exact weight / percentage of total global GDP.
    """
    if pd.isna(country_gdp) or pd.isna(world_gdp) or world_gdp <= 0:
        return np.nan
    return float((country_gdp / world_gdp) * 100.0)


def compute_decade_averages(df_country: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates historical time-series into 10-year macroeconomic performance eras.
    """
    if df_country.empty or 'Year' not in df_country.columns or 'GDP' not in df_country.columns:
        return pd.DataFrame(columns=['Decade', 'Mean_GDP', 'Annual_Growth_Mean'])

    df = df_country.copy()
    df['Decade'] = (df['Year'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + "s"
    df['YoY'] = df['GDP'].pct_change() * 100.0

    summary = df.groupby('Decade_Label').agg(
        Mean_GDP=('GDP', 'mean'),
        Annual_Growth_Mean=('YoY', 'mean'),
        Min_GDP=('GDP', 'min'),
        Max_GDP=('GDP', 'max')
    ).reset_index()

    return summary.sort_values('Decade_Label')


def rank_nations_by_year(df_master: pd.DataFrame, target_year: int) -> pd.DataFrame:
    """
    Ranks all countries globally by audited GDP volume for a specific year.
    """
    year_slice = df_master[df_master['Year'] == target_year].copy()
    if year_slice.empty:
        return pd.DataFrame(columns=['Rank', 'Country Name', 'GDP'])

    year_slice = year_slice.dropna(subset=['GDP'])
    year_slice['Rank'] = year_slice['GDP'].rank(ascending=False, method='min').astype(int)
    
    return year_slice[['Rank', 'Country Name', 'Country Code', 'GDP']].sort_values('Rank')
