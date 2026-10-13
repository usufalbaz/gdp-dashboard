"""
MacroPulse: Global Macroeconomic Intelligence Platform
Engineered quantitative analytics, dynamic nowcasting, and World Bank integration.
"""

import sys
from pathlib import Path
from datetime import datetime

# Inject root for resilient cloud imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.pipeline.loader import load_and_transform_gdp_data
from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility
from src.pipeline.world_bank import WorldBankClient

# Page Setup
st.set_page_config(
    page_title="MacroPulse | Global Economic Engine",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling (Responsive CSS for Mobile & Desktop)
st.markdown("""
<style>
    /* Metric Cards Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .metric-country {
        font-size: 0.95rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .delta-pos { color: #10b981; }
    .delta-neg { color: #ef4444; }
    .vol-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 6px;
        background: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / 'data/gdp_data.csv'

def format_currency(val: float) -> str:
    """Formats large financial metrics cleanly without mobile truncation."""
    if pd.isna(val) or val is None:
        return "N/A"
    abs_val = abs(val)
    if abs_val >= 1e12:
        return f"${val / 1e12:.2f} T"
    elif abs_val >= 1e9:
        return f"${val / 1e9:.2f} B"
    elif abs_val >= 1e6:
        return f"${val / 1e6:.2f} M"
    return f"${val:,.0f}"

@st.cache_data(ttl="1d", show_spinner="Loading historical benchmarks...")
def get_base_dataset() -> pd.DataFrame:
    return load_and_transform_gdp_data(DATA_PATH)

try:
    base_df = get_base_dataset()
except Exception as exc:
    st.error(f"Data pipeline fault: {exc}")
    st.stop()

CURRENT_YEAR = datetime.now().year

# Sidebar Setup
st.sidebar.title("🌍 MacroPulse Engine")
st.sidebar.caption("Macroeconomic Intelligence & Live Synchronization")

st.sidebar.markdown("---")
enable_live_sync = st.sidebar.toggle("⚡ Sync World Bank Live API", value=False)

# Dynamic Dataset Expansion (Real-Time Ingestion if Enabled)
if enable_live_sync:
    wb_client = WorldBankClient(timeout=10)
    st.sidebar.info("🌐 Connected to World Bank Open Data REST API")

all_countries = sorted(base_df['Country Name'].unique())
default_selection = ['United States', 'China', 'Germany', 'Japan', 'Egypt, Arab Rep.']
valid_defaults = [c for c in default_selection if c in all_countries]

selected_countries = st.sidebar.multiselect(
    "Benchmark Nations",
    options=all_countries,
    default=valid_defaults
)

if not selected_countries:
    st.warning("⚠️ Please select at least one nation from the sidebar.")
    st.stop()

# Time Analysis Range (Dynamic up to current year)
min_available_year = int(base_df['Year'].min())
max_available_year = CURRENT_YEAR if enable_live_sync else int(base_df['Year'].max())

from_year, to_year = st.sidebar.slider(
    "Analysis Window",
    min_value=min_available_year,
    max_value=max_available_year,
    value=(1990, max_available_year)
)

# Process country data with dynamic extension
processed_records = []
for country in selected_countries:
    c_df = base_df[base_df['Country Name'] == country].sort_values('Year').copy()
    
    # If live sync enabled, enrich beyond CSV boundaries
    if enable_live_sync and to_year > 2022:
        code_match = c_df['Country Code'].dropna()
        if not code_match.empty:
            iso_code = code_match.iloc[0]
            live_df = wb_client.fetch_indicator(iso_code, start_year=2022, end_year=to_year)
            if not live_df.empty:
                # Merge and drop duplicates
                c_df = pd.concat([c_df, live_df]).drop_duplicates(subset=['Year'], keep='last').sort_values('Year')

    c_df = c_df[(c_df['Year'] >= from_year) & (c_df['Year'] <= to_year)]
    c_df['YoY_Growth'] = calculate_yoy_growth(c_df['GDP'])
    c_df['Rolling_Volatility'] = calculate_volatility(c_df['YoY_Growth'], window=5)
    processed_records.append(c_df)

analytics_df = pd.concat(processed_records) if processed_records else pd.DataFrame()

# Main Header
st.title("🌍 MacroPulse Intelligence Platform")
st.caption(f"Continuous Macroeconomic Profiling (1960–{to_year}) | Automated Growth & Volatility Regime Analysis")

# Modern Tabs
tab_charts, tab_kpi, tab_ledger = st.tabs([
    "📈 Growth & Trajectory", 
    "📊 Econometric Risk & CAGR", 
    "📋 Ledger & Exports"
])

with tab_charts:
    st.subheader("Historical GDP Trajectory (Current US$)")
    fig_gdp = px.line(
        analytics_df,
        x='Year',
        y='GDP',
        color='Country Name',
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_gdp.update_traces(line_shape='spline', line=dict(width=3), marker=dict(size=6))
    fig_gdp.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.25, title=""),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="GDP Volume"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

    st.subheader("Year-over-Year Growth Rate Momentum (%)")
    fig_growth = px.line(
        analytics_df,
        x='Year',
        y='YoY_Growth',
        color='Country Name',
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_growth.update_traces(line_shape='spline', line=dict(width=2))
    fig_growth.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.25, title=""),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="YoY Growth (%)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with tab_kpi:
    st.subheader(f"Macroeconomic Delta & Volatility Index ({from_year} vs {to_year})")
    num_years = to_year - from_year
    
    # Responsive grid: 2 columns on mobile instead of 4 squished columns
    kpi_cols = st.columns(2)
    
    for idx, country in enumerate(selected_countries):
        country_data = analytics_df[analytics_df['Country Name'] == country].sort_values('Year')
        
        start_row = country_data[country_data['Year'] == from_year]
        end_row = country_data[country_data['Year'] == to_year]
        
        start_gdp = start_row['GDP'].values[0] if not start_row.empty else np.nan
        end_gdp = end_row['GDP'].values[0] if not end_row.empty else np.nan
        
        cagr = calculate_cagr(start_gdp, end_gdp, num_years)
        mean_vol = country_data['Rolling_Volatility'].mean()
        
        val_str = format_currency(end_gdp)
        
        if pd.isna(cagr):
            delta_html = "<span class='metric-delta'>N/A</span>"
        else:
            cagr_pct = cagr * 100
            cls = "delta-pos" if cagr_pct >= 0 else "delta-neg"
            arrow = "↑" if cagr_pct >= 0 else "↓"
            delta_html = f"<span class='metric-delta {cls}'>{arrow} {cagr_pct:.2f}% CAGR</span>"
            
        vol_str = f"±{mean_vol:.2f}%" if not pd.isna(mean_vol) else "N/A"
        
        with kpi_cols[idx % 2]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-country">{country}</div>
                <div class="metric-value">{val_str}</div>
                {delta_html}
                <br>
                <span class="vol-badge">🛡️ 5-Yr Volatility: {vol_str}</span>
            </div>
            """, unsafe_allow_html=True)

with tab_ledger:
    st.subheader("Time-Series Analytical Ledger")
    display_cols = ['Country Name', 'Country Code', 'Year', 'GDP', 'YoY_Growth', 'Rolling_Volatility']
    valid_cols = [c for c in display_cols if c in analytics_df.columns]
    
    st.dataframe(
        analytics_df[valid_cols].sort_values(by=['Year', 'GDP'], ascending=[False, False]),
        use_container_width=True
    )
    
    csv_data = analytics_df[valid_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Ledger to CSV",
        data=csv_data,
        file_name=f"macropulse_export_{from_year}_{to_year}.csv",
        mime="text/csv"
    )
