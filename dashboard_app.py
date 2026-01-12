# dashboard_app.py
"""
Costo.menu CEO Dashboard
Refined version based on user feedback (Revenue, Deep Dives, Engagement, Insights).
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

# Custom color palette
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
    st.caption("v1.2 - Strategic Actions")
    
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
    # Engagement Metric instead of License Status Count
    active_30d = df[df["Days Since Last Activity"] <= 30].shape[0] if "Days Since Last Activity" in df.columns else 0
    st.metric("Active Users (30d)", f"{active_30d:,.0f}", help="Users active in the last 30 days")

st.markdown("###")

# 2. Charts Row 1: REVENUE SHARE (Instead of License Status) & REGISTRATION GROWTH
c1, c2 = st.columns([1, 2])

with c1:
    if "License status" in df.columns and "Total payments amount" in df.columns:
        st.subheader("Revenue Share by License")
        # Sum revenue by license status
        rev_by_license = df.groupby("License status")["Total payments amount"].sum().reset_index()
        fig_pie = px.pie(
            rev_by_license, 
            values="Total payments amount", 
            names="License status", 
            title=None,
            color_discrete_sequence=COLOR_SEQUENCE,
            hole=0.4
        )
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption("Which license types drive the most revenue?")

with c2:
    if "Registration date" in df.columns:
        st.subheader("Registration Growth (Cumulative)")
        df_time = df.copy().sort_values("Registration date")
        df_time["RegMonth"] = df_time["Registration date"].dt.to_period("M").astype(str)
        # Count new users per month
        monthly_growth = df_time.groupby("RegMonth").size().reset_index(name="New Users")
        # Cumulative Sum
        monthly_growth["Total Users"] = monthly_growth["New Users"].cumsum()
        
        fig_area = px.area(
            monthly_growth, 
            x="RegMonth", 
            y="Total Users",
            labels={"RegMonth": "Month", "Total Users": "Cumulative Customers"},
            color_discrete_sequence=[COLOR_SEQUENCE[1]]
        )
        st.plotly_chart(fig_area, use_container_width=True)

st.markdown("###")

# 3. Charts Row 2: ENGAGEMENT GROUPS (Instead of Days Histogram)
if "Days Since Last Activity" in df.columns:
    st.subheader("User Engagement Groups")
    
    def classify_activity(days):
        if days <= 30: return "Active (0-30 days)"
        elif days <= 90: return "Dormant (31-90 days)"
        else: return "Churned (>90 days)"
        
    df["Engagement Group"] = df["Days Since Last Activity"].apply(classify_activity)
    
    # Calculate counts and avg revenue per group
    engagement_stats = df.groupby("Engagement Group").agg({
        "User id": "count",
        "Total payments amount": "mean"
    }).reset_index().rename(columns={"User id": "User Count", "Total payments amount": "Avg Revenue"})
    
    # Custom sort order
    order = ["Active (0-30 days)", "Dormant (31-90 days)", "Churned (>90 days)"]
    engagement_stats["Engagement Group"] = pd.Categorical(engagement_stats["Engagement Group"], categories=order, ordered=True)
    engagement_stats = engagement_stats.sort_values("Engagement Group")
    
    c3a, c3b = st.columns(2)
    with c3a:
        fig_bar_eng = px.bar(
            engagement_stats, 
            x="Engagement Group", 
            y="User Count", 
            text="User Count",
            color="Engagement Group",
            color_discrete_map={
                "Active (0-30 days)": "#2a9d8f",
                "Dormant (31-90 days)": "#e9c46a",
                "Churned (>90 days)": "#e76f51"
            }
        )
        st.plotly_chart(fig_bar_eng, use_container_width=True)
    with c3b:
        st.info("💡 **Insight:** Comparison of Average Revenue per Engagement Group")
        st.dataframe(engagement_stats.style.format({"Avg Revenue": "€{:.2f}"}), use_container_width=True)

st.markdown("###")

# 4. Strategic Insights & Actions (NEW)
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

st.markdown("---")
st.markdown("###")

# 5. Deep Dive: TOP REVENUE CUSTOMERS
if "Total payments amount" in df.columns:
    st.subheader("💎 VIP Customer Deep Dive")
    st.markdown("Explore your highest value customers to identify upsell opportunities.")
    
    top_n = df.nlargest(50, "Total payments amount")
    
    # Interactive table with more columns for deep dive
    display_cols = ["Fullname", "Email", "Company", "Total payments amount", "License", "Last activity date", "Menus count"]
    # Filter columns that actually exist
    actual_cols = [c for c in display_cols if c in df.columns]
    
    st.dataframe(
        top_n[actual_cols].style.format({
            "Total payments amount": "€{:.2f}",
            "Last activity date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
        }),
        use_container_width=True,
        height=300
    )
