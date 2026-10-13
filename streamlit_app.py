"""
MacroPulse: Quantitative Macroeconomic Intelligence & Forecasting Engine.
Features continuous nowcasting up to the current calendar year, volatility profiling,
and resilient World Bank data enrichment.
"""

import sys
from pathlib import Path
from datetime import datetime

# Inject root directory for clean package resolution across all cloud runners
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.pipeline.loader import load_and_transform_gdp_data
from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility
from src.pipeline.world_bank import WorldBankClient

# Page Setup
st.set_page_config(
    page_title="MacroPulse | Macro Intelligence Engine",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Financial Dashboard Styling
st.markdown("""
<style>
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 20px;
    }
    .kpi-card {
        flex: 1 1 calc(50% - 12px);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 0.78rem;
        margin-top: 4px;
        font-weight: 600;
    }
    .trend-up { color: #10b981; }
    .trend-down { color: #ef4444; }
    .badge-forecast {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / 'data/gdp_data.csv'
CURRENT_YEAR = datetime.now().year  # Automatically dynamically expands every year

def format_currency(val: float) -> str:
    """Formats financial values concisely for compact responsive mobile displays."""
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

@st.cache_data(ttl="1d", show_spinner="Ingesting benchmark econometric matrix...")
def get_historical_data() -> pd.DataFrame:
    return load_and_transform_gdp_data(DATA_PATH)

try:
    base_df = get_historical_data()
except Exception as exc:
    st.error(f"Runtime Engine Failure: {exc}")
    st.stop()

# Helper: Nowcast / Extrapolate up to the Current Year dynamically
def project_country_gdp(df_country: pd.DataFrame, target_year: int) -> pd.DataFrame:
    """Extrapolates recent growth momentum to project GDP up to the current calendar year."""
    if df_country.empty:
        return df_country
    
    df_sorted = df_country.sort_values('Year').copy()
    last_year = int(df_sorted['Year'].max())
    
    if last_year >= target_year:
        df_sorted['Is_Forecast'] = False
        return df_sorted

    last_val = df_sorted['GDP'].iloc[-1]
    # Calculate weighted trailing growth rate
    recent_growth = df_sorted['GDP'].pct_change().dropna().tail(5).mean()
    if pd.isna(recent_growth) or recent_growth <= -0.5:
        recent_growth = 0.03  # Default fallback 3% baseline growth

    df_sorted['Is_Forecast'] = False
    projected_rows = []
    
    curr_val = last_val
    country_name = df_sorted['Country Name'].iloc[0]
    country_code = df_sorted['Country Code'].iloc[0]

    for yr in range(last_year + 1, target_year + 1):
        curr_val *= (1 + recent_growth)
        projected_rows.append({
            'Country Name': country_name,
            'Country Code': country_code,
            'Year': yr,
            'GDP': curr_val,
            'Is_Forecast': True
        })

    if projected_rows:
        df_projected = pd.DataFrame(projected_rows)
        return pd.concat([df_sorted, df_projected], ignore_index=True)
    
    return df_sorted

# Sidebar
st.sidebar.title("🌐 MacroPulse")
st.sidebar.caption(f"Continuous Horizon (1960–{CURRENT_YEAR})")

all_nations = sorted(base_df['Country Name'].unique())
default_nations = ['Egypt, Arab Rep.', 'United States', 'China', 'Germany']
valid_defaults = [c for c in default_nations if c in all_nations]

selected_nations = st.sidebar.multiselect(
    "Benchmark Nations",
    options=all_nations,
    default=valid_defaults
)

if not selected_nations:
    st.warning("⚠️ Select at least one nation from the sidebar.")
    st.stop()

# Dynamic slider automatically scales up to the current year
from_year, to_year = st.sidebar.slider(
    "Temporal Window",
    min_value=1960,
    max_value=CURRENT_YEAR,
    value=(1995, CURRENT_YEAR)
)

# Process time-series with automatic nowcast extrapolation
nation_frames = []
for nation in selected_nations:
    c_raw = base_df[base_df['Country Name'] == nation]
    c_projected = project_country_gdp(c_raw, CURRENT_YEAR)
    c_filtered = c_projected[(c_projected['Year'] >= from_year) & (c_projected['Year'] <= to_year)].copy()
    
    c_filtered['YoY_Growth'] = calculate_yoy_growth(c_filtered['GDP'])
    c_filtered['Volatility'] = calculate_volatility(c_filtered['YoY_Growth'], window=5)
    nation_frames.append(c_filtered)

analytics_df = pd.concat(nation_frames) if nation_frames else pd.DataFrame()

# Main Interface
st.title("🌐 MacroPulse Economic Platform")
st.markdown(f"**Multi-Decade Macro Trajectory & Econometric Nowcasting ({from_year}–{to_year})** <span class='badge-forecast'>⚡ Dynamic Projections to {CURRENT_YEAR}</span>", unsafe_allow_html=True)

# Top KPI Grid
st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
kpi_cols = st.columns(min(len(selected_nations), 4))

for idx, nation in enumerate(selected_nations):
    n_data = analytics_df[analytics_df['Country Name'] == nation].sort_values('Year')
    if n_data.empty:
        continue
    
    latest_val = n_data['GDP'].iloc[-1]
    is_forecasted = n_data['Is_Forecast'].iloc[-1]
    
    start_val = n_data['GDP'].iloc[0]
    num_yrs = max(to_year - from_year, 1)
    cagr = calculate_cagr(start_val, latest_val, num_yrs)
    
    cagr_str = f"+{cagr*100:.1f}% CAGR" if (cagr and cagr >= 0) else f"{cagr*100:.1f}% CAGR"
    trend_cls = "trend-up" if (cagr and cagr >= 0) else "trend-down"
    tag_forecast = " [Projected]" if is_forecasted else ""

    with kpi_cols[idx % len(kpi_cols)]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{nation}</div>
            <div class="kpi-val">{format_currency(latest_val)}</div>
            <div class="kpi-sub {trend_cls}">{cagr_str}{tag_forecast}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Tabs
tab_gdp, tab_growth, tab_ledger = st.tabs(["📈 GDP Volume & Forecast", "⚡ Growth Momentum (%)", "📋 Ledger & Export"])

PALETTE = ["#38bdf8", "#f43f5e", "#10b981", "#a855f7", "#f59e0b", "#ec4899"]

with tab_gdp:
    st.subheader(f"Gross Domestic Product Trajectory (USD) with Projections to {to_year}")
    fig_gdp = go.Figure()

    for i, nation in enumerate(selected_nations):
        n_df = analytics_df[analytics_df['Country Name'] == nation].sort_values('Year')
        color = PALETTE[i % len(PALETTE)]
        
        # Historical slice
        hist_df = n_df[~n_df['Is_Forecast']]
        if not hist_df.empty:
            fig_gdp.add_trace(go.Scatter(
                x=hist_df['Year'],
                y=hist_df['GDP'],
                name=f"{nation}",
                mode='lines+markers',
                line=dict(color=color, width=3, shape='spline'),
                marker=dict(size=5)
            ))

        # Forecast slice (dashed line)
        fc_df = n_df[n_df['Year'] >= (hist_df['Year'].max() if not hist_df.empty else from_year)]
        if len(fc_df) > 1:
            fig_gdp.add_trace(go.Scatter(
                x=fc_df['Year'],
                y=fc_df['GDP'],
                name=f"{nation} (Projected)",
                mode='lines',
                line=dict(color=color, width=2.5, dash='dash'),
                showlegend=False
            ))

    fig_gdp.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="GDP (Current USD)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Year")
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

with tab_growth:
    st.subheader("Year-over-Year Growth Rate Momentum (%)")
    fig_growth = go.Figure()

    for i, nation in enumerate(selected_nations):
        n_df = analytics_df[analytics_df['Country Name'] == nation].sort_values('Year')
        color = PALETTE[i % len(PALETTE)]

        fig_growth.add_trace(go.Scatter(
            x=n_df['Year'],
            y=n_df['YoY_Growth'],
            name=nation,
            mode='lines',
            line=dict(color=color, width=2.5, shape='spline')
        ))

    fig_growth.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="YoY Growth Rate (%)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Year")
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with tab_ledger:
    st.subheader("Time-Series Macro Ledger")
    clean_table = analytics_df[['Country Name', 'Country Code', 'Year', 'GDP', 'YoY_Growth', 'Is_Forecast']].copy()
    clean_table['GDP_Formatted'] = clean_table['GDP'].apply(format_currency)
    clean_table['YoY_Growth'] = clean_table['YoY_Growth'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
    clean_table['Status'] = clean_table['Is_Forecast'].apply(lambda x: "Projected ⚡" if x else "Verified Historical")

    st.dataframe(
        clean_table[['Country Name', 'Country Code', 'Year', 'GDP_Formatted', 'YoY_Growth', 'Status']]
        .sort_values(by=['Year', 'Country Name'], ascending=[False, True]),
        use_container_width=True
    )
    
    csv_bytes = clean_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Ledger to CSV",
        data=csv_bytes,
        file_name=f"macropulse_data_{from_year}_{to_year}.csv",
        mime="text/csv"
        )
