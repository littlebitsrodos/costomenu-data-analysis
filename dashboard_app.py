# dashboard_app.py
"""
Costo.menu CEO Dashboard
Refined version v1.5 (Simplified + Cohort Revenue + CEO Questions).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Configuration & Branding ---------------------------------------------
st.set_page_config(
    page_title="Costo.menu Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom color palette (Professional Blue/Teal/Orange)
COLOR_SEQUENCE = ["#005f73", "#0a9396", "#94d2bd", "#e9d8a6", "#ee9b00", "#ca6702", "#bb3e03", "#ae2012", "#9b2226"]

# Path to the cleaned CSV
CSV_PATH = Path(__file__).parent / "cleaned_costo_menu.csv"

@st.cache_data
def load_data():
    if not CSV_PATH.exists():
        st.error(f"Data file not found at: {CSV_PATH}")
        return pd.DataFrame()
    
    df = pd.read_csv(CSV_PATH)
    
    # Numeric conversion
    numeric_cols = [
        "Recipe count", "Ingredients count", "Menus count", 
        "Distributors count", "Total payments amount", 
        "Days Since Last Activity", "Customer Lifetime Value"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            
    # Date parsing
    date_cols = ["ExpirationDate", "Last activity date", "Registration date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            
    return df

# --- Load Data ------------------------------------------------------------
df = load_data()
if df.empty:
    st.stop()

# --- Sidebar Filters ------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    if "License status" in df.columns:
        statuses = ["All"] + sorted(df["License status"].dropna().unique().tolist())
        selected_status = st.selectbox("License Status", statuses)
        if selected_status != "All":
            df = df[df["License status"] == selected_status]

    st.markdown("---")
    st.caption("v1.5 - CEO Strategy Edition")
    
    # Download Button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data",
        data=csv_data,
        file_name="costo_menu_cleaned.csv",
        mime="text/csv"
    )

# --- Main Dashboard -------------------------------------------------------
st.title("📊 Costo.menu Executive Dashboard")

# 1. KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Customers", f"{len(df):,.0f}")
with col2:
    total_rev = df["Total payments amount"].sum() if "Total payments amount" in df.columns else 0
    st.metric("Total Revenue", f"€{total_rev:,.2f}")
with col3:
    avg_pay = df["Total payments amount"].mean() if "Total payments amount" in df.columns else 0
    st.metric("Avg Payment", f"€{avg_pay:,.2f}")
with col4:
    active_30d = df[df["Days Since Last Activity"] <= 30].shape[0] if "Days Since Last Activity" in df.columns else 0
    st.metric("Active Users (30d)", f"{active_30d:,.0f}", help="Users active in the last 30 days")

st.markdown("###")

# 2. Charts Row: REGISTRATION GROWTH & REVENUE BY YEAR (COHORT)
if "Registration date" in df.columns:
    st.subheader("User Growth & Cohort Value")
    
    # Prepare data
    df_time = df.copy().sort_values("Registration date")
    df_time["RegMonth"] = df_time["Registration date"].dt.to_period("M").astype(str)
    df_time["RegYear"] = df_time["Registration date"].dt.year
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("**New Registrations per Month**")
        monthly_growth = df_time.groupby("RegMonth").size().reset_index(name="New Users")
        fig_bar = px.bar(
            monthly_growth, 
            x="RegMonth", 
            y="New Users",
            labels={"RegMonth": "Month", "New Users": "Signups"},
            color_discrete_sequence=[COLOR_SEQUENCE[0]]
        )
        fig_bar.update_layout(xaxis_tickangle=-45, margin=dict(t=10, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        if "Total payments amount" in df.columns:
            st.markdown("**Revenue by Registration Year (Cohort LTV)**")
            annual_revenue = df_time.groupby("RegYear")["Total payments amount"].sum().reset_index()
            # Sort by Year just in case
            annual_revenue = annual_revenue.sort_values("RegYear")
            
            fig_rev = px.bar(
                annual_revenue,
                x="RegYear",
                y="Total payments amount",
                labels={"RegYear": "Year", "Total payments amount": "Total Revenue (€)"},
                text="Total payments amount",
                color_discrete_sequence=[COLOR_SEQUENCE[1]]
            )
            fig_rev.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_rev.update_layout(xaxis=dict(tickmode='linear'), margin=dict(t=10, b=0, l=0, r=0))
            st.plotly_chart(fig_rev, use_container_width=True)
            st.caption("Total lifetime revenue generated by users who registered in that year.")

st.markdown("###")

# 3. Strategic Insights & Actions
st.markdown("---")
st.subheader("🚀 Strategic Insights & Recommended Actions")

min_col1, min_col2, min_col3 = st.columns(3)

with min_col1:
    st.error("🚨 Insight: The 'Free Rider' Disconnect")
    st.caption("**Observation:** 4,200+ Active Licenses vs. only €64k Total Revenue.")
    st.caption("**Implication:** High support/server costs for non-paying users.")
    st.info("**Action:** Segment CRM immediately. Separate 'Active & Paying' from 'Active & Free'.")

with min_col2:
    st.warning("💰 Insight: 'Expert' Tier Drivers")
    st.caption("**Observation:** Revenue is highly concentrated in the 'Expert' tier.")
    st.caption("**Implication:** 'Beginner' and many 'Professional' users generate €0.")
    st.info("**Action:** Focus marketing on upselling high-usage 'Professionals' to 'Expert'.")

with min_col3:
    st.error("📉 Insight: Silent Churn Risk")
    st.caption("**Observation:** Missing 'Last Activity' dates default to 0, masking retention issues.")
    st.caption("**Implication:** True retention likely lower than dashboard suggests.")
    st.info("**Action:** Tech Team P0 Fix: Implement reliable `last_login_timestamp` tracking.")

st.markdown("###")

# 4. Deep Dive: TOP REVENUE CUSTOMERS
if "Total payments amount" in df.columns:
    st.subheader("💎 VIP Customer Deep Dive")
    st.markdown("Explore your highest value customers to identify upsell opportunities.")
    
    top_n = df.nlargest(50, "Total payments amount")
    
    display_cols = ["Fullname", "Email", "Company", "Total payments amount", "License", "Last activity date", "Menus count"]
    actual_cols = [c for c in display_cols if c in df.columns]
    
    st.dataframe(
        top_n[actual_cols].style.format({
            "Total payments amount": "€{:.2f}",
            "Last activity date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
        }),
        use_container_width=True,
        height=300
    )

st.markdown("---")

# 5. Strategic Questions for the CEO
st.subheader("🤔 Critical Questions for the CEO")
st.markdown("To ensure the long-term success of Costo.menu, ask yourself these hard questions:")

q1, q2 = st.columns(2)

with q1:
    st.markdown("#### 1. Business vs. Hobby?")
    st.info("We have high traffic but low revenue per user. Are we optimizing for vanity metrics (signups) or value (euros)?")

    st.markdown("#### 2. The Conversion Wall")
    st.info("Why do nearly 0% of users convert to 'Expert' after 1 year? Is the product gap too small, or the price gap too big?")

with q2:
    st.markdown("#### 3. The 'Free' Funnel")
    st.info("Is the Free tier actually a funnel that leads to payment, or just a comfortable parking lot where users stay forever?")

    st.markdown("#### 4. The 'Delete' Test")
    st.info("If we deleted all non-paying accounts today, would anyone notice? If not, why are we paying to host them?")
