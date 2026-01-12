# clean_and_analyze.py
"""
Script to clean the `fouk exel com.xlsx` export from costo.menu, generate a cleaned CSV ready for CRM import,
and produce summary statistics / KPI metrics for the CEO dashboard.
"""

import pandas as pd
from pathlib import Path

# Paths
EXCEL_PATH = Path("fouk exel com.xlsx")
CSV_OUTPUT = Path("cleaned_costo_menu.csv")

def load_excel(path: Path) -> pd.DataFrame:
    # The header row is the second row (index 1) based on inspection
    df = pd.read_excel(path, header=1)
    return df

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_map = {
        "UserSummary_1767798568807": "User ID",
        "Unnamed: 1": "Full Name",
        "Unnamed: 2": "Email",
        "Unnamed: 3": "Phone",
        "Unnamed: 4": "Company",
        "Unnamed: 5": "License Type",
        "Unnamed: 6": "License Expiration",
        "Unnamed: 7": "License Status",
        "Unnamed: 8": "Last Activity",
        "Unnamed: 9": "Recipe Count",
        "Unnamed: 10": "Ingredients Count",
        "Unnamed: 11": "Menus Count",
        "Unnamed: 12": "Distributors Count",
        "Unnamed: 13": "Registration Date",
        "Unnamed: 14": "Total Payments",
    }
    df = df.rename(columns=column_map)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Trim whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Standardise phone numbers – replace missing with "N/A"
    df["Phone"] = df["Phone"].fillna("N/A")

    # Parse dates
    for col in ["License Expiration", "Last Activity", "Registration Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fill missing categorical values (handle possible missing columns)
    if "Company" in df.columns:
        df["Company"] = df["Company"].fillna("Unknown")
    if "License Status" in df.columns:
        df["License Status"] = df["License Status"].fillna("Unknown")

    # Ensure numeric columns are proper numbers
    # Ensure numeric columns are proper numbers (handle possible missing columns)
    numeric_cols = [
        "Recipe Count",
        "Ingredients Count",
        "Menus Count",
        "Distributors Count",
        "Total Payments",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Add derived metrics (handle missing columns)
    if "Last Activity" in df.columns:
        df["Days Since Last Activity"] = (pd.Timestamp("today") - df["Last Activity"]).dt.days
    else:
        df["Days Since Last Activity"] = None
    if "Total Payments" in df.columns:
        df["Customer Lifetime Value"] = df["Total Payments"]
    else:
        df["Customer Lifetime Value"] = None
    return df

def export_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False)

def print_summary(df: pd.DataFrame):
    total_customers = len(df)
    # Safe handling for possible missing columns
    if "License Status" in df.columns:
        active_licenses = (df["License Status"] == "ACTIVE").sum()
    else:
        active_licenses = 0
    if "Total Payments" in df.columns:
        total_revenue = df["Total Payments"].sum()
        avg_payment = df["Total Payments"].mean()
    else:
        total_revenue = 0
        avg_payment = 0
    print("--- Summary Metrics ---")
    print(f"Total customers: {total_customers}")
    print(f"Active licenses: {active_licenses} ({total_customers and active_licenses/total_customers:.2%})")
    print(f"Total revenue (payments): ${total_revenue:,.2f}")
    print(f"Average payment per customer: ${avg_payment:,.2f}")
    # Top 5 customers by payment (if column exists)
    if "Total Payments" in df.columns:
        top5 = df.nlargest(5, "Total Payments")[["User ID", "Full Name", "Total Payments"]]
        print("\nTop 5 customers by payment:")
        print(top5.to_string(index=False))
    else:
        print("\nNo payment data available for top‑customer analysis.")

def main():
    df_raw = load_excel(EXCEL_PATH)
    df = rename_columns(df_raw)
    df = clean_data(df)
    export_csv(df, CSV_OUTPUT)
    print_summary(df)

if __name__ == "__main__":
    main()
