import streamlit as st
import pandas as pd
import json
import plotly.express as px
from pathlib import Path
from difflib import get_close_matches

# --- Load Data Helper ---
def load_invoice_data():
    # 1. Load Invoices
    # Assuming running from root directory
    json_path = Path("invoices.json")
    if not json_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 2. Load CRM Data
    crm_path = Path("cleaned_costo_menu.csv")
    crm_df = pd.DataFrame()
    if crm_path.exists():
        crm_df = pd.read_csv(crm_path)
        # Type cleanup
        if "Total payments amount" in crm_df.columns:
            crm_df["Total payments amount"] = pd.to_numeric(crm_df["Total payments amount"], errors="coerce").fillna(0)
        if "Last activity date" in crm_df.columns:
            crm_df["Last activity date"] = pd.to_datetime(crm_df["Last activity date"], errors="coerce")
    
    # 3. Flatten Invoice Data & Match
    flat_data = []
    
    # Helper for matching
    crm_names = crm_df["Fullname"].dropna().tolist() if not crm_df.empty else []
    
    for inv in data:
        for item in inv["items"]:
            # Coordinate lookup (Mocking a Geocoding API)
            city_coords = {
                "MELISSIA": {"lat": 38.05, "lon": 23.83},
                "RETHYMNO": {"lat": 35.36, "lon": 24.47},
                "THESSALONIKI": {"lat": 40.64, "lon": 22.94},
                "ATHINA": {"lat": 37.98, "lon": 23.72},
                "CHANIA": {"lat": 35.51, "lon": 24.02},
                "KOS": {"lat": 36.89, "lon": 27.28}
            }
            
            # Simple city extraction logic
            cust_addr = inv.get("customer", {}).get("address", "Unknown")
            address = cust_addr.upper()
            city = "Unknown"
            lat, lon = None, None
            
            for k, v in city_coords.items():
                if k in address:
                    city = k.title()
                    lat = v["lat"]
                    lon = v["lon"]
                    break
            if city == "Unknown" and "ATHINA" in address: # Fallback
                city = "Athina"
                lat = city_coords["ATHINA"]["lat"]
                lon = city_coords["ATHINA"]["lon"]

            # --- INTELLIGENCE: MATCHING ---
            inv_name = inv.get("customer", {}).get("name", "Unknown")
            match_name = None
            match_ltv = 0
            match_status = "Unknown"
            match_last_active = None
            
            if crm_names:
                matches = get_close_matches(inv_name, crm_names, n=1, cutoff=0.4)
                if not matches:
                     parts = inv_name.split("/")
                     for p in parts:
                         sub_matches = get_close_matches(p.strip(), crm_names, n=1, cutoff=0.5)
                         if sub_matches:
                             matches = sub_matches
                             break
                
                if matches:
                    match_name = matches[0]
                    # Get CRM details
                    crm_user = crm_df[crm_df["Fullname"] == match_name].iloc[0]
                    match_ltv = crm_user.get("Total payments amount", 0)
                    match_last_active = crm_user.get("Last activity date", pd.NaT)
                    
                    # Status Logic
                    if pd.notnull(match_last_active):
                        days_inactive = (pd.Timestamp.now() - match_last_active).days
                        if days_inactive < 30:
                            match_status = "Active"
                        elif days_inactive < 90:
                            match_status = "At Risk"
                        else:
                            match_status = "Dormant"
                    else:
                        match_status = "Unknown"

            flat_data.append({
                "Date": pd.to_datetime(inv.get("date", pd.Timestamp.now())),
                "Invoice": inv.get("invoice_number", "UNK"),
                "Customer": inv_name,
                "Region": city,
                "Lat": lat,
                "Lon": lon,
                "Package": item.get("description", "Unknown").split(" - ")[0],
                "Amount": item.get("total", 0),
                "CRM_Match": match_name,
                "CRM_LTV": match_ltv,
                "CRM_Status": match_status,
                "CRM_Last_Active": match_last_active
            })
            
    df = pd.DataFrame(flat_data)
    return df, crm_df

def render_page():
    st.title("🧾 Invoice Intelligence")
    st.caption("Auto-matched Invoices with CRM Data")
    st.markdown("---")

    df, crm_df = load_invoice_data()

    if df.empty:
        st.info("No invoice data found. Please place `invoices.json` in the processed folder.")
        # Optional: Button to run processor
        # if st.button("Run Invoice Processor"):
        #     ...
        return

    # --- Top Level Metrics ---
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        total_rev = df["Amount"].sum()
        matched_pct = (df["CRM_Match"].notnull().sum() / len(df)) * 100
        total_ltv_impact = df["CRM_LTV"].sum()
        
        col1.metric("Total Processed Revenue", f"€{total_rev:,.2f}")
        col2.metric("CRM Match Rate", f"{(matched_pct):.0f}%")
        col3.metric("Lifetime Value (Impact)", f"€{total_ltv_impact:,.2f}")
        col4.metric("Invoices Digitized", len(df))

        st.markdown("###")

        # --- Charts Row 1 ---
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("📦 Package vs CRM Status")
            fig_sun = px.sunburst(
                df, 
                path=['Package', 'CRM_Status'], 
                values='Amount',
                color='CRM_Status',
                color_discrete_map={
                    "Active": "#2a9d8f", 
                    "At Risk": "#e9c46a", 
                    "Dormant": "#e76f51", 
                    "Unknown": "#cfcfcf"
                }
            )
            st.plotly_chart(fig_sun, use_container_width=True)
            
        with c2:
            st.subheader("🗺️ Revenue by Region")
            df_geo = df.dropna(subset=["Lat", "Lon"])
            if not df_geo.empty:
                fig_map = px.scatter_mapbox(
                    df_geo, 
                    lat="Lat", 
                    lon="Lon", 
                    size="Amount",
                    color="CRM_Status",
                    hover_name="Customer",
                    hover_data=["Region", "Amount", "CRM_Match"],
                    zoom=5,
                    center={"lat": 38.0, "lon": 23.7},
                    mapbox_style="carto-positron"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No geospatial data found.")

        # --- Intelligence Feed ---
        st.markdown("---")
        st.subheader("🧠 Intelligence Feed")
        
        for idx, row in df.iterrows():
            with st.expander(f"🧾 #{row['Invoice']} - {row['Customer']} (€{row['Amount']})"):
                ic1, ic2 = st.columns(2)
                with ic1:
                    st.markdown(f"**Details**")
                    st.text(f"Date: {row['Date'].date()}")
                    st.text(f"Pkg: {row['Package']}")
                
                with ic2:
                    if row['CRM_Match']:
                        st.success(f"✅ Matched: {row['CRM_Match']}")
                        st.markdown(f"- **Status:** {row['CRM_Status']}")
                        
                        if row['CRM_Status'] == "Dormant":
                            st.error("🚨 **Churn Risk:** User paid but inactive >90d!")
                        elif row['CRM_Status'] == "Unknown" and row['Amount'] > 0:
                            st.warning("⚠️ **Ghost User:** Paying but no tracking data.")
                    else:
                        st.warning("❌ No CRM Match Found.")

        with st.expander("🔎 View Raw Data"):
            st.dataframe(df)
