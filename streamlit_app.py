"""
Global GDP Macroeconomic Intelligence Platform.
Streamlit Controller consuming modular domain engines & risk profiling.
"""

import sys
from pathlib import Path

# Inject root for robust package imports across all runtime environments
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Import core modular engines
from src.pipeline.loader import load_and_transform_gdp_data
from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility

# Page Setup
st.set_page_config(
    page_title="MacroPulse | Global GDP Analytics",
    page_icon="🌍",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / 'data/gdp_data.csv'

@st.cache_data(ttl="1d", show_spinner="Normalizing macroeconomic records...")
def get_dataset() -> pd.DataFrame:
    return load_and_transform_gdp_data(DATA_PATH)

try:
    gdp_df = get_dataset()
except Exception as err:
    st.error(f"Runtime Engine Failure: {err}")
    st.stop()

# Header
st.title("🌍 MacroPulse: Global Macroeconomic Intelligence Platform")
st.caption("Engineered longitudinal econometric profiling (World Bank Dataset 1960–2022) with Volatility & CAGR Risk Indexing")

# Sidebar Filter Controls
st.sidebar.header("Filter & Controls")

min_year = int(gdp_df['Year'].min())
max_year = int(gdp_df['Year'].max())

from_year, to_year = st.sidebar.slider(
    "Analysis Window",
    min_value=min_year,
    max_value=max_year,
    value=(1990, max_year)
)

all_countries = sorted(gdp_df['Country Name'].unique())
default_selection = ['United States', 'China', 'Germany', 'Japan', 'Egypt, Arab Rep.']
valid_defaults = [c for c in default_selection if c in all_countries]

selected_countries = st.sidebar.multiselect(
    "Select Benchmark Nations",
    options=all_countries,
    default=valid_defaults
)

if not selected_countries:
    st.warning("⚠️ Please select at least one nation from the sidebar.")
    st.stop()

# Filter & Enrich with Analytical Metrics
filtered_df = gdp_df[
    (gdp_df['Country Name'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

processed_frames = []
for country in selected_countries:
    c_df = filtered_df[filtered_df['Country Name'] == country].sort_values('Year').copy()
    c_df['YoY_Growth'] = calculate_yoy_growth(c_df['GDP'])
    c_df['Rolling_Volatility'] = calculate_volatility(c_df['YoY_Growth'], window=5)
    processed_frames.append(c_df)

analytics_df = pd.concat(processed_frames) if processed_frames else filtered_df

# Tabs Organization
tab_trends, tab_risk, tab_table = st.tabs([
    "📈 Growth & Trajectory", 
    "📊 Econometric Risk & CAGR", 
    "📋 Ledger & Export"
])

with tab_trends:
    st.subheader("Historical GDP Trajectory (Current US$)")
    fig_gdp = px.line(
        analytics_df,
        x='Year',
        y='GDP',
        color='Country Name',
        markers=True,
        labels={'GDP': 'GDP (USD)', 'Year': 'Year'},
        template="plotly_dark"
    )
    fig_gdp.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig_gdp, use_container_width=True)

    st.subheader("Year-over-Year Growth Rate Momentum (%)")
    fig_growth = px.line(
        analytics_df,
        x='Year',
        y='YoY_Growth',
        color='Country Name',
        markers=True,
        labels={'YoY_Growth': 'YoY Growth Rate (%)', 'Year': 'Year'},
        template="plotly_dark"
    )
    fig_growth.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig_growth, use_container_width=True)

with tab_risk:
    st.subheader(f"Macroeconomic Delta & Volatility Profile ({from_year} vs {to_year})")
    num_years = to_year - from_year
    cols = st.columns(min(len(selected_countries), 4))
    
    for idx, country in enumerate(selected_countries):
        country_data = analytics_df[analytics_df['Country Name'] == country].sort_values('Year')
        
        start_row = country_data[country_data['Year'] == from_year]
        end_row = country_data[country_data['Year'] == to_year]
        
        start_gdp = start_row['GDP'].values[0] if not start_row.empty else np.nan
        end_gdp = end_row['GDP'].values[0] if not end_row.empty else np.nan
        
        cagr = calculate_cagr(start_gdp, end_gdp, num_years)
        mean_volatility = country_data['Rolling_Volatility'].mean()
        
        with cols[idx % len(cols)]:
            display_val = f"${end_gdp / 1e9:,.2f} B" if not pd.isna(end_gdp) else "N/A"
            cagr_delta = f"{cagr * 100:.2f}% CAGR" if not pd.isna(cagr) else "N/A"
            st.metric(label=country, value=display_val, delta=cagr_delta)
            
            vol_label = f"±{mean_volatility:.2f}%" if not pd.isna(mean_volatility) else "N/A"
            st.caption(f"🛡️ 5-Yr Volatility Index: **{vol_label}**")

with tab_table:
    st.subheader("Normalized Time-Series Ledger")
    st.dataframe(
        analytics_df[['Country Name', 'Country Code', 'Year', 'GDP', 'YoY_Growth', 'Rolling_Volatility']]
        .sort_values(by=['Year', 'GDP'], ascending=[False, False]),
        use_container_width=True
    )
