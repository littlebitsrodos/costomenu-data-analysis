import pandas as pd
import json
import datetime

def clean_date(val):
    if pd.isna(val):
        return ""
    if isinstance(val, datetime.datetime):
        return val.isoformat()
    return str(val)

try:
    # Read Excel, skipping the first row (header is at index 1)
    df = pd.read_excel("fouk exel com.xlsx", header=1)
    
    # Map columns
    column_mapping = {
        "User id": "UserID",
        "Fullname": "Fullname",
        "Company": "Company",
        "License": "LicenseType",
        "ExpirationDate": "ExpirationDate",
        "License status": "Status",
        "Recipe count": "RecipeCount",
        "Ingredients count": "IngredientCount",
        "Distributors count": "DistributorCount",
        "Total payments amount": "TotalPayments"
    }
    
    # Select and rename
    df_clean = df[column_mapping.keys()].rename(columns=column_mapping)
    
    # Fill NaN
    df_clean["RecipeCount"] = df_clean["RecipeCount"].fillna(0)
    df_clean["IngredientCount"] = df_clean["IngredientCount"].fillna(0)
    df_clean["DistributorCount"] = df_clean["DistributorCount"].fillna(0)
    df_clean["TotalPayments"] = df_clean["TotalPayments"].fillna(0)
    df_clean["Company"] = df_clean["Company"].fillna("Unknown")
    df_clean["LicenseType"] = df_clean["LicenseType"].fillna("Beginner")
    df_clean["Status"] = df_clean["Status"].fillna("Inactive")
    
    # Handle dates
    df_clean["ExpirationDate"] = df_clean["ExpirationDate"].apply(clean_date)
    
    # Convert to list of dicts
    data = df_clean.to_dict(orient="records")
    
    # Generate TS content
    ts_content = """export interface User {
  UserID: string | number;
  Fullname: string;
  Company: string;
  LicenseType: string;
  ExpirationDate: string;
  Status: string;
  RecipeCount: number;
  IngredientCount: number;
  DistributorCount: number;
  TotalPayments: number;
}

export const data: User[] = """ + json.dumps(data, indent=2) + ";"

    with open("costomenu-bi/src/lib/data.ts", "w") as f:
        f.write(ts_content)
        
    print("Successfully generated costomenu-bi/src/lib/data.ts")

except Exception as e:
    print(f"Error generating data: {e}")
