import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="Global GDP Analytics Engine",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data(ttl="1d")
def load_and_transform_gdp_data(filepath: Path) -> pd.DataFrame:
    """
    Loads raw World Bank GDP data and melts year columns into a normalized time-series dataframe.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found at: {filepath}")

    raw_df = pd.read_csv(filepath)
    
    # Identify year columns (1960 to 2022)
    year_columns = [col for col in raw_df.columns if col.isdigit()]
    
    # Normalized melting
    melted_df = raw_df.melt(
        id_vars=['Country Name', 'Country Code'],
        value_vars=year_columns,
        var_name='Year',
        value_name='GDP'
    )
    
    melted_df['Year'] = pd.to_numeric(melted_df['Year'], errors='coerce')
    melted_df['GDP'] = pd.to_numeric(melted_df['GDP'], errors='coerce')
    
    return melted_df

def calculate_cagr(start_val: float, end_val: float, num_years: int) -> float:
    """Calculates Compound Annual Growth Rate (CAGR)."""
    if num_years <= 0 or start_val <= 0 or pd.isna(start_val) or pd.isna(end_val):
        return np.nan
    return ((end_val / start_val) ** (1 / num_years)) - 1

# Load Data
DATA_PATH = Path(__file__).parent / 'data/gdp_data.csv'
try:
    gdp_df = load_and_transform_gdp_data(DATA_PATH)
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# Header
st.title("🌍 Global GDP Macroeconomic Intelligence Platform")
st.caption("Engineered time-series analysis & comparative macroeconomic insights (World Bank Data 1960–2022)")

# Sidebar Controls
st.sidebar.header("Filter & Controls")

min_year = int(gdp_df['Year'].min())
max_year = int(gdp_df['Year'].max())

from_year, to_year = st.sidebar.slider(
    "Analysis Window",
    min_value=min_year,
    max_value=max_year,
    value=(1990, max_year)
)

all_countries = sorted(gdp_df['Country Name'].dropna().unique())
default_selection = ['United States', 'China', 'Germany', 'Japan', 'United Kingdom', 'Egypt, Arab Rep.']
valid_defaults = [c for c in default_selection if c in all_countries]

selected_countries = st.sidebar.multiselect(
    "Select Nations for Comparison",
    options=all_countries,
    default=valid_defaults
)

if not selected_countries:
    st.warning("⚠️ Please select at least one nation from the sidebar.")
    st.stop()

# Filter Data
filtered_df = gdp_df[
    (gdp_df['Country Name'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# Tabs Organization
tab_trends, tab_comparison, tab_table = st.tabs(["📈 Growth & Trajectory", "📊 Comparative Metrics", "📋 Raw Data"])

with tab_trends:
    st.subheader("Historical GDP Trajectory (Current US$)")
    fig = px.line(
        filtered_df,
        x='Year',
        y='GDP',
        color='Country Name',
        markers=True,
        labels={'GDP': 'GDP (USD)', 'Year': 'Year'},
        template="plotly_dark"
    )
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

with tab_comparison:
    st.subheader(f"Macroeconomic Delta Summary ({from_year} vs {to_year})")
    
    num_years = to_year - from_year
    cols = st.columns(min(len(selected_countries), 4))
    
    for idx, country in enumerate(selected_countries):
        country_data = gdp_df[gdp_df['Country Name'] == country]
        
        start_row = country_data[country_data['Year'] == from_year]
        end_row = country_data[country_data['Year'] == to_year]
        
        start_gdp = start_row['GDP'].values[0] if not start_row.empty else np.nan
        end_gdp = end_row['GDP'].values[0] if not end_row.empty else np.nan
        
        cagr = calculate_cagr(start_gdp, end_gdp, num_years)
        
        with cols[idx % len(cols)]:
            display_val = f"${end_gdp / 1e9:,.2f} B" if not pd.isna(end_gdp) else "N/A"
            cagr_delta = f"{cagr * 100:.2f}% CAGR" if not pd.isna(cagr) else "N/A"
            st.metric(label=country, value=display_val, delta=cagr_delta)

with tab_table:
    st.subheader("Tabular Dataset Exploration")
    st.dataframe(
        filtered_df.sort_values(by=['Year', 'GDP'], ascending=[False, False]),
        use_container_width=True
)
