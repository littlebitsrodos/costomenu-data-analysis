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

# --- Sidebar Navigation ---------------------------------------------------
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ["Business Overview", "Support Analytics", "Sales Intelligence"])
    
    st.markdown("---")

# --- Page 1: Business Overview --------------------------------------------
if page == "Business Overview":
    # --- Sidebar Filters (Business) ---------------------------------------
    with st.sidebar:
        st.header("Filters & Segments")
        
        # 1. License Type Filter (Custom Order)
        if "License" in df.columns:
            # Define the exact order requested
            desired_order = ["Beginner", "Professional", "Expert"]
            # distinct_licenses = df["License"].dropna().unique().tolist() # Unused if we force list, but good for checking
            
            # Create list: All + Ordered items (if they exist in data) + any others
            options = ["All"] + [x for x in desired_order if x in df["License"].unique()]
            
            # Add any others found in data but not in our list (just in case)
            # others = [x for x in df["License"].dropna().unique() if x not in desired_order]
            # options += sorted(others)
            
            selected_license = st.radio("Select Segment:", options) # User asked to "Rearrange", Radio is cleaner for 4 items
            
            if selected_license != "All":
                df = df[df["License"] == selected_license]

        st.markdown("---")
        
        # 2. Dynamic Segment Metrics
        st.subheader("📊 Segment Snapshot")
        
        # Safe calculations
        seg_users = len(df)
        seg_rev = df["Total payments amount"].sum() if "Total payments amount" in df.columns else 0
        seg_avg_rev = seg_rev / seg_users if seg_users > 0 else 0
        seg_avg_recipes = df["Recipe count"].mean() if "Recipe count" in df.columns else 0
        
        st.metric("Users in Segment", f"{seg_users:,.0f}")
        st.metric("Avg Revenue", f"€{seg_avg_rev:,.2f}")
        st.metric("Avg Recipes", f"{seg_avg_recipes:,.1f}")
        
        st.markdown("---")
        st.caption("v2.0 - Simplified Segmentation")
        
        # Download Button
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv_data,
            file_name="costo_menu_filtered.csv",
            mime="text/csv"
        )

    # --- Main Dashboard -------------------------------------------------------
    st.title("📊 Costo.menu Executive Dashboard")

    # 1. User Health Pulse (Top Priority)
    if "Last activity date" in df.columns:
        st.subheader("❤️ User Health Pulse")
        
        # Calculate Segments based on Date (ignoring the pre-filled 0s in numeric col)
        # We use a fresh calculation to safely identify 'Unknown'
        current_date = pd.Timestamp.now()
        
        # Function to bucket users
        def get_status(date_val):
            if pd.isna(date_val):
                return "⚪ Unknown"
            diff = (current_date - date_val).days
            if diff <= 30:
                return "🟢 Active (≤30d)"
            elif diff <= 90:
                return "🟡 At Risk (31-90d)"
            else:
                return "🔴 Dormant (>90d)"

        df["Health_Status"] = df["Last activity date"].apply(get_status)
        
        # Determine context for custom advice (moved up for use in Chart + Table)
        current_selection = "All"
        if "License" in df.columns and len(df["License"].unique()) == 1:
                current_selection = df["License"].unique()[0]

        # Group for Pie Chart
        health_counts = df["Health_Status"].value_counts().reset_index()
        health_counts.columns = ["Status", "Count"] # Rename for clarity
        
        # Custom Hover Text Logic
        def get_hover_desc(status):
            if "Unknown" in status:
                if current_selection == "Beginner":
                    return "<b>Why Unknown?</b><br>No 'Last Activity' date found.<br>Likely abandoned account."
                elif current_selection == "Professional":
                     return "<b>Why Unknown?</b><br>No 'Last Activity' date found.<br>⚠️ Paying user with no tracking!"
                elif current_selection == "Expert":
                    return "<b>Why Unknown?</b><br>No 'Last Activity' date found.<br>🚨 Critical data gap for VIP."
                else:
                    return "<b>Why Unknown?</b><br>Value is 'NaN'.<br>Tracking pixel didn't fire."
            elif "Active" in status:
                 return "<b>Status:</b> Active in last 30 days."
            elif "At Risk" in status:
                 return "<b>Status:</b> No activity for 31-90 days."
            elif "Dormant" in status:
                 return "<b>Status:</b> Inactive for >90 days."
            return ""

        health_counts["Description"] = health_counts["Status"].apply(get_hover_desc)
        
        # Define colors mapping
        color_map = {
            "🟢 Active (≤30d)": "#2a9d8f",  # Green
            "🟡 At Risk (31-90d)": "#e9c46a", # Yellow
            "🔴 Dormant (>90d)": "#e76f51",   # Red
            "⚪ Unknown": "#cfcfcf"          # Grey
        }
        
        col_health_1, col_health_2 = st.columns([1, 1])
        
        with col_health_1:
             fig_health = px.pie(
                health_counts,
                values="Count",
                names="Status",
                color="Status",
                color_discrete_map=color_map,
                hole=0.4,
                custom_data=["Description"]
            )
             fig_health.update_traces(
                 textposition='inside', 
                 textinfo='percent+label',
                 hovertemplate="<b>%{label}</b><br>Count: %{value}<br><br>%{customdata[0]}<extra></extra>"
             )
             fig_health.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
             st.plotly_chart(fig_health, use_container_width=True)

        with col_health_2:
            st.markdown("##### 🩺 Retention Strategy")
            # Dynamic Strategy Table based on Filter
            # Default Strategies
            strat_active = "**Protect.** These are your power users. Engage them personally."
            strat_risk = "**Save.** They are drifting. Send a 'New Feature' email *now*."
            strat_dormant = "**Wake Up.** Re-engagement campaign."
            
            # Dynamic 'Unknown' Strategy
            strat_unknown = "**Fix.** Fix the tracking bug. Half your users are invisible." # Default
            
            # (Already calculated above)
                 
            if current_selection == "Beginner":
                strat_unknown = "**Clean.** Likely abandoned accounts. Safe to archive/delete?"
            elif current_selection == "Professional":
                strat_unknown = "**Investigate.** Support Risk! Paying users with no data. Reach out."
            elif current_selection == "Expert":
                strat_unknown = "**Concierge.** Call them. High-value blind spot."

            st.markdown(f"""
            | Segment | Strategy |
            | :--- | :--- |
            | **🟢 Active** | {strat_active} |
            | **🟡 At Risk** | {strat_risk} |
            | **🔴 Dormant** | {strat_dormant} |
            | **⚪ Unknown** | {strat_unknown} |
            """)
            
            # Dynamic Insight based on the current filtered segment
            unknown_users = df[df["Health_Status"] == "⚪ Unknown"]
            unknown_count = len(unknown_users)
            
            if unknown_count > 0:
                if current_selection == "Beginner":
                    st.info(f"🕵️ **Zombie Accounts:** The 'Unknown' slice contains **{unknown_count}** Beginners with no activity data. They are likely abandoned/inactive accounts.")
                elif current_selection == "Professional":
                     st.warning(f"⚠️ **Blind Spot:** We have **{unknown_count}** Paying Professionals with no recent activity data. We can't tell if they are at risk of churning!")
                elif current_selection == "Expert":
                    st.error(f"🚨 **Critical Blank:** **{unknown_count}** Expert users are paying top dollar but have no activity tracked. Verify manually immediately.")
                else:
                     st.info(f"ℹ️ **Data Gap:** {unknown_count} users have no activity tracking enabled.")

    st.markdown("###")

    st.markdown("###")

    # 3. The Value Matrix: Usage vs. Revenue
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
            *   **Goal:** Move people from Bottom-Right (Freeloaders) to Top-Right (Power Users).
            """)

    st.markdown("###")

    # 4. KPIs (Moved Down)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Customers", f"{len(df):,.0f}")
    with col2:
        active_30d = df[df["Days Since Last Activity"] <= 30].shape[0] if "Days Since Last Activity" in df.columns else 0
        st.metric("Active Users (30d)", f"{active_30d:,.0f}", help="Users active in the last 30 days")

    st.markdown("###")

    # 5. User Growth & Seasonality
    if "Registration date" in df.columns:
        st.subheader("User Growth & Value")
        
        # Prepare data for Seasonality
        df_season = df.copy()
        df_season = df_season.dropna(subset=["Registration date"])
        df_season["Month_Num"] = df_season["Registration date"].dt.month
        df_season["Month_Name"] = df_season["Registration date"].dt.month_name()
        df_season["Year"] = df_season["Registration date"].dt.year.astype(str)
        
        # Group by Year + Month
        seasonality = df_season.groupby(["Year", "Month_Num", "Month_Name"]).size().reset_index(name="New Users")
        seasonality = seasonality.sort_values(["Year", "Month_Num"])
        
        st.markdown("##### Seasonality: Registrations by Month (Year-over-Year)")
        
        fig_season = px.line(
            seasonality,
            x="Month_Name",
            y="New Users",
            color="Year",
            markers=True,
            labels={"Month_Name": "Month", "New Users": "New Signups", "Year": "Year"},
            color_discrete_sequence=px.colors.qualitative.Prism  # Distinct colors for years
        )
        
        # Fix X-axis order to be Jan-Dec
        months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        fig_season.update_xaxes(categoryorder="array", categoryarray=months_order)
        fig_season.update_layout(margin=dict(t=10, b=0, l=0, r=0))
        
        st.plotly_chart(fig_season, use_container_width=True)

        with st.expander("ℹ️ How to think about this graph"):
            st.markdown("""
            **What you are seeing:** Each line represents a year. The X-axis is January-December.
            
            **How to interpret seasonality:**
            *   **Spikes:** Do we always peak in a certain month? (e.g., Pre-Summer season?).
            *   **Trend:** Is the 2025 line higher than the 2024 line? (Growth).
            *   **Seasonality:** If every line dips in August, that's a seasonal pattern we can't fight.
            """)

    st.markdown("###")

    # 4. Strategic Insights & Actions
    st.markdown("---")
    st.subheader("🚀 Strategic Insights & Recommended Actions")

    min_col1, min_col2, min_col3 = st.columns(3)

    with min_col1:
        st.error("🚨 Insight: The 'Free Rider' Disconnect")
        st.caption("**Observation:** 4,200+ Active Licenses. Support is given via Phone, Crisp, Email & In-App.")
        st.caption("**Risk:** We are spending resources across 4 channels on users who pay €0.")
        st.info("**Action:** Restrict 'Phone/Crisp' support to Paid tiers. Automate the rest.")

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
            width='stretch',
            height=300
        )

    st.markdown("---")

    # 6. ex-KMN Users (Professional + No Expiration)
    if "License" in df.columns and "ExpirationDate" in df.columns:
        st.subheader("👻 ex-KMN Users")
        st.markdown("**Criteria:** License = 'Professional' AND Expiration Date is Missing.")
        
        ex_kmn = df[
            (df["License"] == "Professional") & 
            (df["ExpirationDate"].isna())
        ].copy()
        
        if "Last activity date" in ex_kmn.columns:
            ex_kmn = ex_kmn.sort_values("Last activity date", ascending=False)
        
        st.caption(f"Found {len(ex_kmn)} users matching these criteria.")
        
        kmn_cols = ["Fullname", "Email", "Company", "Last activity date", "Recipe count", "Total payments amount"]
        kmn_actual = [c for c in kmn_cols if c in ex_kmn.columns]
        
        st.dataframe(
            ex_kmn[kmn_actual].style.format({
                "Last activity date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else "",
                "Total payments amount": "€{:.2f}"
            }),
            width='stretch',
            height=300
        )

    st.markdown("---")

    # 7. Strategic Sandbox
    st.subheader("🧪 CEO Sandbox: What If?")
    st.markdown("Don't just guess. Simulate the impact of strategic decisions on your bottom line.")

    # Layout: Tabs for different scenarios
    tab1, tab2, tab3 = st.tabs(["💰 Revenue Simulator", "🗑️ Cost of Inaction", "👥 Funnel Reality"])

    # --- TAB 1: Revenue Simulator ---
    with tab1:
        st.markdown("#### Scenario: What if we improved conversion?")
        st.info("Currently, most users are on the Free tier. Small improvements in conversion yield massive returns.")
        
        col_sim_1, col_sim_2 = st.columns(2)
        
        with col_sim_1:
            # Calculate current metrics
            total_users = len(df)
            paid_users = df[df["Total payments amount"] > 0].shape[0]
            current_conversion = (paid_users / total_users) * 100 if total_users > 0 else 0
            current_avg_revenue = df[df["Total payments amount"] > 0]["Total payments amount"].mean() if paid_users > 0 else 0
            
            st.metric(
                "Current Conversion Rate", 
                f"{current_conversion:.2f}%",
                help="Formula: (Paying Users / Total Users) * 100"
            )
            st.metric(
                "Avg Revenue per Paying User", 
                f"€{current_avg_revenue:.2f}",
                help="Formula: Total Revenue / Paying Users"
            )

        with col_sim_2:
            # Interactive Sliders
            target_conversion = st.slider(
                "Target Conversion Rate (%)", 
                min_value=0.0, 
                max_value=10.0, 
                value=float(round(current_conversion, 1) + 1.0),
                step=0.1,
                format="%.1f%%"
            )
            
            # Calculation
            projected_paid_users = int(total_users * (target_conversion / 100))
            new_paid_users = projected_paid_users - paid_users
            projected_revenue_gain = new_paid_users * current_avg_revenue
            
            if new_paid_users > 0:
                st.success(f"🎯 **Result:** Converting **{new_paid_users}** more users generates an extra **€{projected_revenue_gain:,.2f}** per year.")
            elif new_paid_users < 0:
                st.error(f"📉 **Warning:** Dropping to {target_conversion}% means losing **{abs(new_paid_users)}** customers and **€{abs(projected_revenue_gain):,.2f}** in revenue.")
            else:
                st.info("No change in projected revenue.")

    # --- TAB 2: Cost of Inaction ---
    with tab2:
        st.markdown("#### Scenario: How much is 'Free' costing us?")
        st.warning("Hosting, support, and storage aren't free. Inactive users are a hidden tax on the business.")
        
        col_cost_1, col_cost_2 = st.columns(2)
        
        with col_cost_1:
            # Identify "Ghost" users (Active > 90 days ago or never active)
            if "Days Since Last Activity" in df.columns:
                ghost_users = df[df["Days Since Last Activity"] > 90].shape[0]
            else:
                ghost_users = 0
                
            st.metric("Ghost Users (>90 days inactive)", f"{ghost_users:,.0f}", delta_color="inverse")
            
        with col_cost_2:
            cost_per_user = st.number_input(
                "Est. Annual Cost per User (€) (Server + Support)", 
                min_value=0.1, 
                value=1.50, 
                step=0.1,
                format="%.2f"
            )
            
            burn_rate = ghost_users * cost_per_user
            st.error(f"🔥 **Burn Rate:** We are wasting **€{burn_rate:,.2f}/year** supporting inactive accounts.")
            
    # --- TAB 3: Funnel Reality ---
    with tab3:
        st.markdown("#### Scenario: The 'Real' Funnel")
        st.markdown("See how your userbase shrinks when you filter out the noise.")
        
        start_metric = len(df)
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.metric("1. Total Signups", f"{start_metric:,.0f}")
            
        with c2:
            # Interactive Toggle
            strict_mode = st.toggle("Strict Mode (Active in last 30 days)", value=True)
            
            if strict_mode:
                 if "Days Since Last Activity" in df.columns:
                    mid_metric = df[df["Days Since Last Activity"] <= 30].shape[0]
                    label = "2. Active Users (30d)"
                 else:
                    mid_metric = 0
                    label = "Last Activity Unknown"
            else:
                mid_metric = df[df["License status"] == "Professional"].shape[0] # Fallback proxy if toggle off
                label = "2. Professional Licenses"
                
            drop_off = ((start_metric - mid_metric) / start_metric) * 100 if start_metric > 0 else 0
            st.metric(label, f"{mid_metric:,.0f}", delta=f"-{drop_off:.1f}% Drop", delta_color="inverse")

        with c3:
            end_metric = df[df["Total payments amount"] > 0].shape[0]
            final_conv = ((end_metric / start_metric) * 100) if start_metric > 0 else 0
            st.metric("3. Paying Customers", f"{end_metric}", delta=f"{final_conv:.2f}% Conversion")

# --- Page 2: Support Intelligence -----------------------------------------
elif page == "Support Analytics":
    st.title("🛡️ Support Analytics")
    st.markdown("Analysis of **370** processed tickets.")
    
    # Paths to generated CSVs
    TOPICS_CSV = Path(__file__).parent / "ticket_topics.csv"
    TIMING_CSV = Path(__file__).parent / "ticket_timing.csv"
    CATEGORIES_CSV = Path(__file__).parent / "categorized_tickets.csv"
    
    # Check if files exist
    if not TOPICS_CSV.exists() or not TIMING_CSV.exists() or not CATEGORIES_CSV.exists():
        st.error("Missing analysis data! Please run the Python analysis scripts first.")
        st.stop()
        
    topic_df = pd.read_csv(TOPICS_CSV)
    time_df = pd.read_csv(TIMING_CSV)
    cat_df = pd.read_csv(CATEGORIES_CSV)
    
    # Load Response Times
    RESPONSE_CSV = Path(__file__).parent / "response_times.csv"
    if RESPONSE_CSV.exists():
        resp_df = pd.read_csv(RESPONSE_CSV)
    else:
        resp_df = pd.DataFrame()
        st.warning("Run analyze_response_time.py to see Response Time metrics.")
    
    # Ensure Sentiment columns exist (backward compatibility)
    if "Sentiment" not in cat_df.columns:
        cat_df["Sentiment"] = "Neutral"
    if "Sentiment Score" not in cat_df.columns:
        cat_df["Sentiment Score"] = 0.0
    
    # --- Top Metrics ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    top_cat = cat_df["Category"].mode()[0]
    error_pct = (cat_df[cat_df["Category"] == "Error"].shape[0] / len(cat_df)) * 100
    
    with col_kpi1:
        st.metric("Total Tickets Processed", f"{len(cat_df)}")
    with col_kpi2:
        st.metric("Top Complaint", top_cat)
    with col_kpi3:
        st.metric("Error Rate", f"{error_pct:.1f}%", delta="High", delta_color="inverse")
        
    # Sentiment KPI
    avg_sentiment = cat_df["Sentiment Score"].mean()
    sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
    sentiment_color = "normal" if sentiment_label == "Positive" else "inverse"
    
    st.markdown("---")
    
    col_sent_1, col_sent_2 = st.columns(2)
    with col_sent_1:
         st.metric("Overall Sentiment Score", f"{avg_sentiment:.2f}", delta=sentiment_label, delta_color=sentiment_color)
    with col_sent_2:
        neg_count = cat_df[cat_df["Sentiment"] == "Negative"].shape[0]
        st.metric("Negative Tickets", f"{neg_count}", delta="Requires Attention", delta_color="inverse")
        
    st.markdown("---")
    
    # --- Visuals ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Ticket Categories")
        cat_counts = cat_df["Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        
        fig_cat = px.pie(cat_counts, values="Count", names="Category", hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with c2:
        st.subheader("Volume by Hour")
        # Filter timings
        hour_data = time_df[time_df["Type"] == "HourOfDay"].copy()
        
        fig_time = px.bar(
            hour_data, 
            x="Key", 
            y="Count", 
            labels={"Key": "Hour", "Count": "Tickets"},
            color="Count",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # Sentiment Breakdown
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Sentiment Distribution")
        sent_counts = cat_df["Sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        
        # Color Map
        sent_colors = {"Positive": "#2a9d8f", "Neutral": "#e9c46a", "Negative": "#e76f51"}
        
        fig_sent = px.pie(
            sent_counts, 
            values="Count", 
            names="Sentiment", 
            hole=0.4,
            color="Sentiment",
            color_discrete_map=sent_colors
        )
        st.plotly_chart(fig_sent, use_container_width=True)
        
        st.info("💡 **Tip:** Click on the 'Negative' slice to see what people are complaining about.")
        
    st.markdown("###")
    
    # --- Response Time Analysis ---
    if not resp_df.empty:
        st.subheader("⏱️ Response Times & SLA Analysis")
        
        # Metrics
        avg_resp = resp_df["AvgResponseMinutes"].mean()
        peak_hr = resp_df.loc[resp_df["AvgResponseMinutes"].idxmax()]
        
        c_resp1, c_resp2, c_resp3 = st.columns(3)
        c_resp1.metric("Avg First Response", f"{avg_resp:.1f} mins", delta="-5m vs Target" if avg_resp < 30 else "Above Target", delta_color="normal" if avg_resp < 30 else "inverse")
        c_resp2.metric("Slowest Hour", f"{int(peak_hr['Hour']):02d}:00", f"{peak_hr['AvgResponseMinutes']:.1f}m")
        c_resp3.info("**Goal:** Respond within 30 minutes during business hours.")
        
        # Viz using Column Chart with Color Threshold
        resp_df["Is_Breach"] = resp_df["AvgResponseMinutes"] > 30
        
        fig_resp = px.bar(
            resp_df,
            x="Hour",
            y="AvgResponseMinutes",
            title="Average Response Time by Hour of Day",
            labels={"AvgResponseMinutes": "Mins to Respond", "Hour": "Hour of Day"},
            color="AvgResponseMinutes",
            color_continuous_scale=["#2a9d8f", "#e9c46a", "#e76f51"], # Green to Red
            range_color=[0, 60] # Normalize color scale 0-60 mins
        )
        # Add SLA Line
        fig_resp.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="SLA Target (30m)")
        fig_resp.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
        
        st.plotly_chart(fig_resp, use_container_width=True)

    st.markdown("###")
    
    # --- Advanced Intelligence: Who is complaining? ---
    st.subheader("🧠 Deep Dive: Who is asking?")
    
    # Merge with User Data to get License info
    # Ensure Emails are lowercase/trimmed for matching
    if "Email" in cat_df.columns and "Email" in df.columns:
        cat_df['Email_Clean'] = cat_df['Email'].astype(str).str.lower().str.strip()
        df['Email_Clean'] = df['Email'].astype(str).str.lower().str.strip()
        
        merged_df = pd.merge(
            cat_df, 
            df[['Email_Clean', 'License', 'License status', 'Total payments amount']], 
            left_on='Email_Clean', 
            right_on='Email_Clean', 
            how='left'
        )
        
        merged_df['License'] = merged_df['License'].fillna('Unknown / Non-User')
        
        # Viz: Categories by License
        lic_cat_counts = merged_df.groupby(['License', 'Category']).size().reset_index(name='Count')
        
        # Force Order for Licenses
        license_order = ["Beginner", "Professional", "Expert", "Unknown / Non-User"]
        
        fig_lic = px.bar(
            lic_cat_counts, 
            x="License", 
            y="Count", 
            color="Category", 
            title="Ticket Volume by License Tier",
            category_orders={"License": license_order},
            height=400
        )
        st.plotly_chart(fig_lic, use_container_width=True)
        
        # Metric: High Value Support Burden
        expert_tickets = merged_df[merged_df['License'] == 'Expert'].shape[0]
        st.caption(f"💡 **Insight:** Your **Expert** users created **{expert_tickets}** tickets. Check the table below to prioritize them.")
        
    st.markdown("###")

    # --- Data Explorer ---
    st.subheader("🔍 Ticket Explorer")
    
    col_filter_1, col_filter_2 = st.columns(2)
    
    with col_filter_1:
        selected_cat = st.selectbox("Filter by Category", ["All"] + list(cat_counts["Category"]))
        
    with col_filter_2:
        # User license options
        lic_opts = ["All", "Beginner", "Professional", "Expert", "Unknown"]
        selected_lic = st.selectbox("Filter by License", lic_opts)
        
    selected_sentiment = st.selectbox("Filter by Sentiment", ["All", "Negative", "Neutral", "Positive"])
    
    # Prepare display dataframe with License info
    display_df = cat_df.copy()
    
    # Merge if not already merged in the 'Deep Dive' section
    if "License" not in display_df.columns:
        if "Email" in display_df.columns and "Email" in df.columns:
            # Quick merge for the table
            tmp_user = df.copy()
            tmp_user['Email_Clean'] = tmp_user['Email'].astype(str).str.lower().str.strip()
            display_df['Email_Clean'] = display_df['Email'].astype(str).str.lower().str.strip()
            
            display_df = pd.merge(
                display_df,
                tmp_user[['Email_Clean', 'License']],
                on='Email_Clean',
                how='left'
            )
            display_df['License'] = display_df['License'].fillna('Unknown')
    
    # Apply Filters
    if selected_cat != "All":
        display_df = display_df[display_df["Category"] == selected_cat]
        
    if selected_lic != "All":
        # Handle 'Unknown' specifically
        if selected_lic == "Unknown":
            display_df = display_df[display_df["License"].isna() | (display_df["License"] == "Unknown")]
        else:
            display_df = display_df[display_df["License"] == selected_lic]
            
    if selected_sentiment != "All":
        display_df = display_df[display_df["Sentiment"] == selected_sentiment]
        
    # Create a unique key for the dataframe to avoid state issues
    # We want to enable selection
    event = st.dataframe(
        display_df[["Date", "Category", "Sentiment", "User", "License", "First Message"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, HH:mm", width="medium"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Sentiment": st.column_config.TextColumn("Sentiment", width="small"),
            "User": st.column_config.TextColumn("User", width="medium"),
            "License": st.column_config.TextColumn("License", width="small"),
            "First Message": st.column_config.TextColumn("First Message", width="large"),
        },
        on_select="rerun",
        selection_mode="single-row",
        height=400
    )
    
    # --- Interaction: User History Pop-up ---
    # Check if a row was selected
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        selected_row = display_df.iloc[selected_index]
        selected_user = selected_row["User"]
        selected_email_clean = str(selected_row.get("Email_Clean", "")).strip().lower()
        
        st.markdown("---")
        st.subheader(f"👤 Customer 360: {selected_user}")
        
        col_360_1, col_360_2 = st.columns([1, 2])
        
        with col_360_1:
            st.info(f"**License:** {selected_row.get('License', 'Unknown')}")
            # Find stats from original df if possible
            if "Email_Clean" in df.columns:
                 user_stats = df[df["Email_Clean"] == selected_email_clean]
                 if not user_stats.empty:
                     u_stat = user_stats.iloc[0]
                     st.write(f"**Total Spend:** €{u_stat.get('Total payments amount', 0):.2f}")
                     st.write(f"**Recipes:** {u_stat.get('Recipe count', 0)}")
                     st.write(f"**Last Active:** {u_stat.get('Last activity date', 'Unknown')}")
        
        with col_360_2:
            st.markdown("**📜 Ticket History**")
            # Find all tickets for this user
            user_tickets = cat_df[cat_df["User"] == selected_user].sort_values("Date", ascending=False)
            
            for i, ticket in user_tickets.iterrows():
                with st.expander(f"{ticket['Date']} - {ticket['Category']} ({ticket.get('Sentiment', 'Neutral')})"):
                    st.write(f"**Message:** {ticket['First Message']}")
                    st.caption(f"Session ID: {ticket['Session ID']}")
    
    # Download Action
    csv_exp = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Support Data",
        data=csv_exp,
        file_name="support_tickets_filtered.csv",
        mime="text/csv"
    )

# --- Page 3: Sales Intelligence -------------------------------------------
elif page == "Sales Intelligence":
    import modules.sales_intelligence as sales_module
    sales_module.render_page()
