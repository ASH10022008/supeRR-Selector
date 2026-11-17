import streamlit as st
import pandas as pd
import plotly.express as px
from pressure_engine import compute_pressure_and_rankings

# 1. Page Configuration
st.set_page_config(
    page_title="RR Analytics | Clutch Performance Engine",
    page_icon="",
    layout="wide"
)

# 2. Custom Rajasthan Royals Theme (Royal Blue & Pink Injection)
st.markdown("""
    <style>
    /* Main background & Font */
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .rr-header {
        background: linear-gradient(135deg, #1b264f 0%, #0d1117 100%);
        border-bottom: 3px solid #ea1a66;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(234, 26, 102, 0.15);
    }
    
    .rr-title {
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    .rr-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
    }
    
    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161b22;
        padding: 8px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        color: #8b949e;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ea1a66 !important;
        color: white !important;
    }
    
    /* Dataframe & Metric Cards */
    div[data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 8px;
        background-color: #161b22;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def get_rankings():
    return compute_pressure_and_rankings()

# Retrieve full ranked datasets
all_batters, all_bowlers = get_rankings()

# Extract Top 10 slices for Tab 1 leaderboards
top_batters = all_batters.head(10)
top_bowlers = all_bowlers.head(10)

# Create display labels so ONLY the Top 10 names appear as text on the full scatter plot
all_batters['display_label'] = [name if idx < 10 else '' for idx, name in enumerate(all_batters['player_name'])]
all_bowlers['display_label'] = [name if idx < 10 else '' for idx, name in enumerate(all_bowlers['player_name'])]

# App Header with RR Branding
st.markdown("""
    <div class="rr-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 class="rr-title" style="margin: 0; font-size: 2.2rem;"> Rajasthan Royals: Clutch Analytics Engine</h1>
                <p class="rr-subtitle" style="margin: 5px 0 0 0;">Official Data-Driven System Identifying High-Pressure Performers (Season 2)</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([" Top 10 Rankings", " Clutch Quadrant Analysis", " Methodology & Parameters"])

with tab1:
    st.subheader("Final Unstop Submission Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###  Top 10 Batters Under Pressure")
        bat_display = top_batters.reset_index(drop=True)
        bat_display.index += 1
        st.dataframe(bat_display[['player_name', 'sr_normal', 'sr_pressure', 'league_avg_pressure_sr', 'clutch_impact', 'clutch_score']], use_container_width=True)
        
    with col2:
        st.markdown("###  Top 10 Bowlers Under Pressure")
        bowl_display = top_bowlers.reset_index(drop=True)
        bowl_display.index += 1
        st.dataframe(bowl_display[['player_name', 'econ_normal', 'econ_pressure', 'league_avg_pressure_econ', 'wickets_pressure', 'clutch_impact', 'clutch_score']], use_container_width=True)

with tab2:
    st.subheader("Performance Delta Scatter Plot (Baseline vs. Pressure)")
    st.markdown("Showing all qualified players across the dataset. Elite performers in the top-right/bottom-left quadrants elevate their game when stakes peak.")
    
    metric_choice = st.selectbox("Select Category", ["Batters (Strike Rate)", "Bowlers (Economy Rate)"])
    
    # Custom Plotly Template matching RR's Dark Theme
    rr_template = {
        "layout": {
            "paper_bgcolor": "#0d1117",
            "plot_bgcolor": "#161b22",
            "font": {"color": "#f0f6fc"},
            "xaxis": {"gridcolor": "#30363d", "zerolinecolor": "#30363d"},
            "yaxis": {"gridcolor": "#30363d", "zerolinecolor": "#30363d"}
        }
    }
    
    if "Batters" in metric_choice:
        fig = px.scatter(
            all_batters, x='sr_normal', y='sr_pressure',
            text='display_label', hover_name='player_name',
            size='balls_pressure', color='clutch_score',
            labels={'sr_normal': 'Baseline Strike Rate', 'sr_pressure': 'High-Pressure Strike Rate'},
            title="Batter Clutch Performance Matrix (All Qualified Players)",
            color_continuous_scale="RdPu"
        )
        fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='#ea1a66')))
        fig.update_layout(template=rr_template)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.scatter(
            all_bowlers, x='econ_normal', y='econ_pressure',
            text='display_label', hover_name='player_name',
            size='balls_pressure', color='clutch_score',
            labels={'econ_normal': 'Baseline Economy', 'econ_pressure': 'High-Pressure Economy'},
            title="Bowler Clutch Performance Matrix (All Qualified Players - Lower Economy is Better)",
            color_continuous_scale="Purp"
        )
        fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='#1b264f')))
        fig.update_layout(template=rr_template)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("How Pressure is Operationalized")
    st.markdown("""
    * **Match Phase Context:** Isolating deliveries in death overs (Overs 16–20) where run-rate pressure peaks.

    * **Collapse Situations:** Factoring in innings status when top-order wickets fall early.

    * **Sample Size Controls:** Applying logarithmic weighting to ensure players with high variance across tiny samples do not skew leaderboards.

    * **Batter clutch impact:** (pressure strike rate - league-average pressure strike rate) + 0.2 × (pressure strike rate - normal strike rate).

    * **Bowler clutch impact:** 15 × (league-average pressure economy - pressure economy) + 3 × (normal economy - pressure economy) + (pressure wickets / pressure balls × 36) × 10.

    * **League benchmark:** Delivery-weighted across all high-pressure deliveries: total pressure runs / pressure balls × 100 for strike rate, or × 6 for economy.

    * **Final score:** Clutch impact × ln(1 + pressure balls) × ln(1 + pressure matches) × average stakes weight × average recency weight.

    * **Eligibility:** At least 30 normal deliveries and 20 high-pressure deliveries.
    """)
