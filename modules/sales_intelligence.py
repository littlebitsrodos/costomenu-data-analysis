import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Configuration ---
SALES_EXPORT_PATH = Path("SalesExport_23_1_2026.xls")
CRM_DATA_PATH = Path("cleaned_costo_menu.csv")

@st.cache_data
def load_crm_data():
    if not CRM_DATA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CRM_DATA_PATH)
    if 'Email' in df.columns:
        df['Email_Clean'] = df['Email'].astype(str).str.lower().str.strip()
    return df

@st.cache_data
def load_viva_sales():
    if not SALES_EXPORT_PATH.exists():
        return pd.DataFrame()
    
    try:
        # Viva exports are HTML tables renamed to .xls
        df_list = pd.read_html(SALES_EXPORT_PATH, decimal=',', thousands='.')
        if not df_list:
            return pd.DataFrame()
        
        df = df_list[0]
        # Clean column names
        df.columns = [c.strip() for c in df.columns]
        
        # Basic cleaning for 'Ποσό' (Amount)
        if 'Ποσό' in df.columns:
            # Handle potential Excel-style string prefixes like ='161.20'
            df['Amount_Clean'] = df['Ποσό'].astype(str).str.replace('=', '').str.replace('"', '').str.replace("'", "").str.strip().astype(float)
        
        # Clean 'Ημ/νία' (Date)
        if 'Ημ/νία' in df.columns:
            df['Date_Clean'] = pd.to_datetime(df['Ημ/νία'], dayfirst=True, errors='coerce')
        
        if 'E-mail' in df.columns:
            df['Email_Clean'] = df['E-mail'].astype(str).str.lower().str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error loading Sales Export: {e}")
        return pd.DataFrame()

def render_page():
    st.title("💰 Viva Sales Intelligence")
    st.markdown("Live Sales Data from **Viva Payments** Export.")
    
    # Load Data
    viva_df = load_viva_sales()
    crm_df = load_crm_data()
    
    if viva_df.empty:
        st.warning("No sales data found in `SalesExport_23_1_2026.xls`.")
        return

    # Filter for Successful Transactions
    success_df = viva_df[viva_df['Κατάσταση'] == 'Επιτυχημένη'].copy()
    
    # Year Filter
    if 'Date_Clean' in success_df.columns:
        success_df['Year'] = success_df['Date_Clean'].dt.year
        years = sorted(success_df['Year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("Select Year:", ["All"] + [str(y) for y in years])
        
        if selected_year != "All":
            success_df = success_df[success_df['Year'] == int(selected_year)]

    # --- Reconciliation logic ---
    if not crm_df.empty and 'Email_Clean' in success_df.columns:
        # Join to find matches
        merged = pd.merge(
            success_df, 
            crm_df[['Email_Clean', 'Fullname', 'License', 'License status']], 
            on='Email_Clean', 
            how='left'
        )
        match_count = merged['Fullname'].notna().sum()
        match_rate = (match_count / len(success_df)) * 100
        unmatched_df = merged[merged['Fullname'].isna()]
    else:
        match_count = 0
        match_rate = 0
        unmatched_df = pd.DataFrame()

    # --- Top Level Metrics ---
    total_rev = success_df['Amount_Clean'].sum()
    total_trans = len(success_df)
    avg_ticket = total_rev / total_trans if total_trans > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Revenue", f"€{total_rev:,.2f}")
    m2.metric("Successful Transactions", total_trans)
    m3.metric("Avg. Sale Value", f"€{avg_ticket:,.2f}")
    
    st.markdown("---")

    # --- Reconciliation Explorer ---
    st.subheader("🔗 CRM Reconciliation")
    r1, r2, r3 = st.columns(3)
    r1.metric("CRM Match Rate", f"{match_rate:.1f}%")
    r2.metric("Matched Customers", match_count)
    r3.metric("Unknown Buyers", len(unmatched_df))

    with st.expander("Why are some buyers unknown?"):
        st.markdown("""
        **Unmatched transactions** usually represent:
        1. **New Customers:** People who just bought but aren't in the last Excel export yet.
        2. **Email Mismatch:** They used a different email for payment than the one in their account.
        3. **Ghost Sales:** Legacy or manual adjustments.
        """)

    if not unmatched_df.empty:
        st.warning(f"Found {len(unmatched_df)} transactions from emails not found in CRM.")
        st.dataframe(
            unmatched_df[['Ημ/νία', 'E-mail', 'Περιγραφή Εμπόρου', 'Ποσό']], 
            use_container_width=True, 
            hide_index=True
        )

    st.markdown("---")
    
    # --- Visuals ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Sales by Product")
        # Clean up description (remove =" prefix)
        success_df['Product'] = success_df['Περιγραφή Εμπόρου'].str.replace('=', '').str.replace('"', '').str.strip()
        prod_stats = success_df.groupby('Product')['Amount_Clean'].sum().reset_index()
        fig_pie = px.pie(prod_stats, values='Amount_Clean', names='Product', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("Revenue Trend")
        # Group by Date
        daily_rev = success_df.groupby('Date_Clean')['Amount_Clean'].sum().reset_index()
        daily_rev = daily_rev.sort_values('Date_Clean')
        fig_line = px.line(daily_rev, x='Date_Clean', y='Amount_Clean', markers=True, 
                          labels={'Date_Clean': 'Date', 'Amount_Clean': 'Daily Revenue (€)'})
        st.plotly_chart(fig_line, use_container_width=True)

    # --- Data Explorer ---
    st.subheader("🔍 Transaction Log")
    
    log_cols = ['Ημ/νία', 'Ώρα', 'E-mail', 'Περιγραφή Εμπόρου', 'Ποσό']
    st.dataframe(
        success_df[log_cols].sort_values('Ημ/νία', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Intelligence Snippet
    st.info("💡 **Insight:** Renewals (Professional/Expert) are the most frequent transactions. Consider a targeted campaign for 'Beginner' users to 'Professional' upgrade.")
