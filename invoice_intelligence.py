import streamlit as st
import pandas as pd
import json
import plotly.express as px
from pathlib import Path
from difflib import get_close_matches

# --- Configuration ---
st.set_page_config(
    page_title="Costo.menu Invoice Intelligence",
    page_icon="🧾",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    # 1. Load Invoices
    json_path = Path("invoices.json")
    if not json_path.exists():
        st.error("invoices.json not found!")
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
            address = inv["customer"]["address"].upper()
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
            inv_name = inv["customer"]["name"]
            match_name = None
            match_ltv = 0
            match_status = "Unknown"
            match_last_active = None
            
            # 1. Try exact name match (normalized)
            # 2. Try fuzzy match
            if crm_names:
                # Basic normalization for matching
                matches = get_close_matches(inv_name, crm_names, n=1, cutoff=0.4) # Low cutoff as invoice names are messy (e.g. UPPERCASE legal)
                
                # Check specific overrides/better matching logic if fuzzy fails or needs help
                if not matches:
                    # Try splitting invoice name (e.g. "Name / Company")
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
                "Date": pd.to_datetime(inv["date"]),
                "Invoice": inv["invoice_number"],
                "Customer": inv_name,
                "Region": city,
                "Lat": lat,
                "Lon": lon,
                "Package": item["description"].split(" - ")[0],
                "Amount": item["total"],
                "CRM_Match": match_name,
                "CRM_LTV": match_ltv,
                "CRM_Status": match_status,
                "CRM_Last_Active": match_last_active
            })
            
    df = pd.DataFrame(flat_data)
    return df, crm_df

# Helper: Greek to Latin Transliteration
def normalize_name(text):
    if not isinstance(text, str):
        return ""
    
    text = text.upper()
    
    # Simple Greek -> Latin mapping (basic)
    replacements = {
        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'I', 'Θ': 'TH',
        'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P',
        'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F', 'Χ': 'X', 'Ψ': 'PS', 'Ω': 'O',
        'Ά': 'A', 'Έ': 'E', 'Ή': 'I', 'Ί': 'I', 'Ό': 'O', 'Ύ': 'Y', 'Ώ': 'O',
        'ΟΥ': 'OU' # Dipthong
    }
    
    # Phonetic fix for MP -> B (common in names like Bakalis/Mpakalis)
    # Applied before single char replacement if possible, or generally on the string
    # BUT we must be careful. Let's do it after basic mapping or add "ΜΠ" keys.
    # Let's add explicit dipthongs first
    replacements_phonetic = {
        'ΜΠ': 'B', 'ΝΤ': 'D'
    }
    for k, v in replacements_phonetic.items():
        text = text.replace(k, v)

    for k, v in replacements.items():
        text = text.replace(k, v)
        
    # Remove Legal Noise
    noise = [" IKE", " E.E", " A.E", " O.E", " LTD", " ESTIATORIO", " ZAXAROPLASTEIO", " E ESTIASI", " / "]
    for n in noise:
        text = text.replace(n, " ")
        
    return text.strip()

def find_best_match(target, choices):
    # 1. Normalize Target
    norm_target = normalize_name(target)
    target_tokens = set(t for t in norm_target.split() if len(t) > 2) # Ignore short tokens
    
    best_match = None
    best_score = 0
    
    for choice in choices:
        norm_choice = normalize_name(choice)
        choice_tokens = set(t for t in norm_choice.split() if len(t) > 2)
        
        # Scoring: Jaccard Similarity of Tokens + Substring Boost
        score = 0
        matches_found = 0
        total_tokens = len(target_tokens)
        
        if total_tokens == 0: continue

        for t_tok in target_tokens:
            for c_tok in choice_tokens:
                # Exact Token Match
                if t_tok == c_tok:
                    score += 1.0
                    matches_found += 1
                # Substring Match (Strong)
                elif len(t_tok) > 3 and len(c_tok) > 3 and (t_tok in c_tok or c_tok in t_tok):
                    score += 0.8 # High confidence for distinct substring (e.g. BAKAL in BAKALIS)
                    matches_found += 1
        
        # Final normalized score
        final_score = score / max(len(target_tokens), len(choice_tokens), 1)
        
        if final_score > best_score:
            best_score = final_score
            best_match = choice
            
    # Threshold
    if best_score > 0.3: # Slightly lower threshold for substring logic
        return best_match
    return None

df, crm_df = load_data()

# --- Header ---
st.title("🧾 Costo.menu Invoice Intelligence")
st.caption("v0.3 - Smart Matching (Greek/Latin + Entity Resolution)")
st.markdown("---")

# --- Top Level Metrics ---
if not df.empty:
    # RE-RUN MATCHING LOGIC HERE (Simulated Post-Process for cleaner code refactor)
    # Ideally this goes in load_data but for the edit, we apply it to the DF
    crm_names = crm_df["Fullname"].dropna().unique().tolist()
    
    refined_matches = []
    refined_ltvs = []
    refined_statuses = []
    refined_dates = []

    for idx, row in df.iterrows():
        match = find_best_match(row["Customer"], crm_names)
        
        if match:
             # Get CRM details
            crm_user = crm_df[crm_df["Fullname"] == match].iloc[0]
            r_ltv = crm_user.get("Total payments amount", 0)
            r_last = crm_user.get("Last activity date", pd.NaT)
            
            # Status Logic
            r_status = "Unknown"
            if pd.notnull(r_last):
                days_inactive = (pd.Timestamp.now() - r_last).days
                if days_inactive < 30:
                    r_status = "Active"
                elif days_inactive < 90:
                    r_status = "At Risk"
                else:
                    r_status = "Dormant"
            
            refined_matches.append(match)
            refined_ltvs.append(r_ltv)
            refined_statuses.append(r_status)
            refined_dates.append(r_last)
        else:
            refined_matches.append(None)
            refined_ltvs.append(0)
            refined_statuses.append("Unknown")
            refined_dates.append(None)
            
    df["CRM_Match"] = refined_matches
    df["CRM_LTV"] = refined_ltvs
    df["CRM_Status"] = refined_statuses
    df["CRM_Last_Active"] = refined_dates

# --- Top Level Metrics ---
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_rev = df["Amount"].sum()
    avg_order = df["Amount"].mean()
    matched_pct = (df["CRM_Match"].notnull().sum() / len(df)) * 100
    total_ltv_impact = df["CRM_LTV"].sum()
    
    col1.metric(
        "Total Processed Revenue", 
        f"€{total_rev:,.2f}",
        help="Sum of all invoice totals in this batch."
    )
    col2.metric(
        "CRM Match Rate", 
        f"{(matched_pct):.0f}%",
        help="Percentage of invoices linked to a known CRM user."
    )
    col3.metric(
        "Lifetime Value (Impact)", 
        f"€{total_ltv_impact:,.2f}", 
        help="Total historical value of these specific customers (from CRM)."
    )
    col4.metric(
        "Invoices Digitized", 
        len(df),
        help="Count of unique documents processed."
    )

    st.markdown("###")

    # --- Charts Row 1 ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("📦 Package vs CRM Status")
        # Visualizing who is buying what and if they are active
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
                color="CRM_Status", # Changed to Status to see where active users are
                hover_name="Customer",
                hover_data=["Region", "Amount", "CRM_Match"],
                zoom=5,
                center={"lat": 38.0, "lon": 23.7},
                mapbox_style="carto-positron"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No geospatial data found (check address formatting).")

    # --- Intelligence Insights ---
    st.markdown("---")
    st.subheader("🧠 Intelligence Feed")
    
    # Detailed Matches
    for idx, row in df.iterrows():
        with st.expander(f"🧾 Invoice #{row['Invoice']} - {row['Customer']} (€{row['Amount']})"):
            ic1, ic2 = st.columns(2)
            with ic1:
                st.markdown(f"**Invoice Details**")
                st.text(f"Date: {row['Date'].date()}")
                st.text(f"Package: {row['Package']}")
                st.text(f"Region: {row['Region']}")
            
            with ic2:
                if row['CRM_Match']:
                    st.success(f"✅ **Matched to CRM User:** {row['CRM_Match']}")
                    st.markdown(f"- **Lifetime Value:** €{row['CRM_LTV']:,.2f}")
                    st.markdown(f"- **Status:** {row['CRM_Status']}")
                    last_act = row['CRM_Last_Active'].date() if pd.notnull(row['CRM_Last_Active']) else "Never"
                    st.markdown(f"- **Last Seen:** {last_act}")
                    
                    # Intelligence Logic
                    if row['CRM_Status'] == "Dormant":
                        st.error("🚨 **Churn Risk:** User just paid but hasn't logged in for >90 days! Invoice might be automated renewal.")
                    elif row['CRM_Status'] == "Unknown" and row['Amount'] > 0:
                        st.warning("⚠️ **Ghost User:** Paying customer but no activity tracking found.")
                    elif row['CRM_LTV'] > (row['Amount'] * 2):
                         st.info("💎 **Loyal Customer:** LTV is significantly higher than this single invoice.")
                else:
                    st.warning("❌ **No CRM Match Found.** New customer or different legal name?")

    # --- Raw Data ---
    with st.expander("🔎 View Raw Extracted JSON Data"):
        st.dataframe(df)
