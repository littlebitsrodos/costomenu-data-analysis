# dashboard_app.py
"""
Costo.menu CEO Dashboard
Refined version v1.8 (Added Explanatory Text & Guides).
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
    st.caption("v1.8 - Educational Guides")
    
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

# 2. Charts Section
if "Registration date" in df.columns:
    st.subheader("User Growth & Value")
    
    # Prepare data
    df_time = df.copy().sort_values("Registration date")
    df_time["RegMonth"] = df_time["Registration date"].dt.to_period("M").astype(str)
    df_time["RegYear"] = df_time["Registration date"].dt.year
    
    # Chart 1: Registrations (Full Width)
    st.markdown("##### New Registrations per Month")
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

    with st.expander("ℹ️ How to think about this graph"):
        st.markdown("""
        **What you are seeing:** The raw number of new users signing up for the platform each month.
        
        **How to interpret it:** 
        *   **Rising bars:** Healthy top-of-funnel growth. Marketing is working.
        *   **Flat/Declining bars:** We are stalling on acquisition. We need new channels.
        *   *Note: This does not show retention, only new blood entering the system.*
        """)
    
    st.markdown("###")
    
    # Chart 2: Revenue by Cohort (Full Width)
    if "Total payments amount" in df.columns:
        st.markdown("##### Revenue by Registration Year (Cohort LTV)")
        annual_revenue = df_time.groupby("RegYear")["Total payments amount"].sum().reset_index()
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
        fig_rev.update_layout(xaxis=dict(tickmode='linear', type='category'), margin=dict(t=10, b=0, l=0, r=0))
        st.plotly_chart(fig_rev, use_container_width=True)
        
        # Tooltip / Definition for Cohort LTV
        st.info("**Definition: Cohort LTV (Lifetime Value)** groups users by the year they joined and sums up *all* the money they have paid us since then.")
        
        with st.expander("ℹ️ How to think about this graph"):
            st.markdown("""
            **What you are seeing:** The total financial value of each "Vintage" of customers.
            
            **How to interpret it:**
            *   **Older bars should be huge:** Users from 2021 have had 5 years to pay us. If their bar is small, our long-term retention is poor.
            *   **Newer bars will be smaller:** Users from 2026 just arrived.
            *   **The Goal:** We want to see the 2025/2026 bars growing *faster* than the 2021 bars did at the same age (indicating better monetization).
            """)

st.markdown("###")

# 3. Value Matrix (Scatter Plot)
if "Recipe count" in df.columns and "Total payments amount" in df.columns:
    st.subheader("The Value Matrix: Usage vs. Revenue")
    
    fig_scatter = px.scatter(
        df, 
        x="Recipe count", 
        y="Total payments amount",
        color="License status" if "License status" in df.columns else None,
        hover_data=["Fullname", "Email", "Company"],
        labels={"Recipe count": "Usage (Recipe Count)", "Total payments amount": "Total Revenue (€)"},
        color_discrete_sequence=COLOR_SEQUENCE,
        opacity=0.6,
        height=500
    )
    fig_scatter.update_traces(marker=dict(size=8))
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    with st.expander("ℹ️ How to think about this graph"):
        st.markdown("""
        **What you are seeing:** Every dot is a single customer. 
        *   **X-Axis:** How much they use the tool (Recipe Count).
        *   **Y-Axis:** How much they pay us (Total Revenue).
        
        **The 4 Quadrants:**
        *   **Top-Right (High Usage, High Pay):** 🌟 **Power Users.** Clone these people.
        *   **Bottom-Right (High Usage, Low Pay):** 💸 **Freeloaders.** They love the product but don't pay. Upsell target #1.
        *   **Top-Left (Low Usage, High Pay):** ⚠️ **At Risk.** They pay but don't use it. They will churn soon.
        *   **Bottom-Left (Low Usage, Low Pay):** 👻 **Ghosts.** Irrelevant.
        """)

st.markdown("###")

# 4. Strategic Insights & Actions
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
    st.subheader("💎 VIP Customer Deep Dive (> €200)")
    st.markdown("Customers with total lifetime payments exceeding €200.")
    
    # Filter for > 200 EUR
    top_n = df[df["Total payments amount"] > 200].sort_values("Total payments amount", ascending=False).reset_index(drop=True)
    top_n.index += 1  # Start ranking from 1
    
    display_cols = ["Fullname", "Email", "Company", "Total payments amount", "License", "License status", "Last activity date", "Menus count", "Recipe count"]
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

# 6. Strategic Questions for the CEO
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
