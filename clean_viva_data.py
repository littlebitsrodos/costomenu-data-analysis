import pandas as pd
import os
import glob
from bs4 import BeautifulSoup

# Define directories
DATA_DIR = "Viva - SalesExport"
OUTPUT_FILE = "cleaned_viva_sales_all_time.csv"

# Column Mapping (Greek -> English)
COLUMN_MAPPING = {
    'Ημ/νία': 'Date',
    'Ποσό': 'Amount',
    'Προμήθεια': 'Commission',
    'Καθαρό ποσό Εμπόρου': 'Net Amount',
    'Κωδ. Συν/γης (Viva)': 'Transaction ID',
    'Περιγραφή Πηγής': 'Source Description',
    'Περιγραφή Πελάτη': 'Customer Description',
    'E-mail': 'Email',
    'Τύπος': 'Type',
    'Κατάσταση': 'Status'
}

def parse_file(file_path):
    """
    Parses a Viva sales export file. 
    Handles both HTML-masked-as-XLS and real XLSX files.
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        df = None
        # Check if it's the 2026 file or any real xlsx
        if ext == '.xlsx':
            # Likely a real Excel file
            try:
                # Try reading as Excel first
                df = pd.read_excel(file_path)
            except Exception:
                # Fallback to HTML if it fails (unlikely for .xlsx but possible)
                print(f"  -> Read as Excel failed for {filename}, trying HTML...")
        
        # If not loaded yet, try as HTML (legacy exports)
        if df is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            dfs = pd.read_html(content, decimal=',', thousands='.')
            if dfs:
                df = dfs[0]

        if df is None:
            print(f"Warning: Could not parse {filename}")
            return None
            
        # Cleanup Column Names
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        
        # Rename columns using map
        df = df.rename(columns=COLUMN_MAPPING)
        
        return df

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def clean_dataframe(df):
    """
    Applies standard cleaning to the aggregated dataframe.
    """
    # 1. Handle Dates
    # The date format in the file seems to be DD/MM/YYYY based on "24/12/2024"
    if 'Date' in df.columns:
        df['Date_Cleaned'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        # If coerce failed for some, it might be due to time inclusion or format diffs in excel
        if df['Date_Cleaned'].isnull().sum() > 0:
             # Try generic parsing for remaining
             mask = df['Date_Cleaned'].isnull() & df['Date'].notnull()
             df.loc[mask, 'Date_Cleaned'] = pd.to_datetime(df.loc[mask, 'Date'], infer_datetime_format=True, dayfirst=True, errors='coerce')
    else:
        print("Warning: 'Date' column not found.")

    # 2. Handle Amounts (Amount, Commission, Net Amount)
    monetary_cols = ['Amount', 'Commission', 'Net Amount']
    
    for col in monetary_cols:
        if col in df.columns:
            # If it's object type, try to convert strings "1.234,56" -> 1234.56 or "161,20" -> 161.20
            if df[col].dtype == 'object':
                 df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                 df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 3. Clean Text Fields which might have excel formulas like ="String"
    for col in df.select_dtypes(include=['object']).columns:
        # Check if column has values starting with =" and ending with "
        df[col] = df[col].astype(str).str.replace(r'^="', '', regex=True).str.replace(r'"$', '', regex=True).str.strip()
        df[col] = df[col].replace({'nan': None, 'None': None, '': None})

    return df

def main():
    all_dfs = []
    
    # Find all matching files
    search_pattern = os.path.join(DATA_DIR, "SalesExport_*")
    files = sorted(glob.glob(search_pattern))
    
    # Filter for xls/xlsx only
    files = [f for f in files if f.endswith('.xls') or f.endswith('.xlsx')]

    if not files:
        print(f"No files found matching {search_pattern}")
        return

    print(f"Found {len(files)} files to process.")
    
    for file_path in files:
        print(f"Processing {os.path.basename(file_path)}...")
        df = parse_file(file_path)
        if df is not None:
            df['Source_File'] = os.path.basename(file_path)
            all_dfs.append(df)
            print(f"  -> Found {len(df)} rows.")

    if not all_dfs:
        print("No data extracted.")
        return

    # Merge all
    full_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Total raw rows: {len(full_df)}")
    
    # Clean
    cleaned_df = clean_dataframe(full_df)
    
    # Deduplicate
    if 'Transaction ID' in cleaned_df.columns:
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(subset=['Transaction ID'])
        print(f"Dropped {initial_count - len(cleaned_df)} duplicates based on 'Transaction ID'.")
    else:
        print("Warning: 'Transaction ID' column not found (after rename). Skipping strict deduplication.")
        print("Columns present:", cleaned_df.columns.tolist())
        cleaned_df = cleaned_df.drop_duplicates()

    # Sort by date
    if 'Date_Cleaned' in cleaned_df.columns:
        cleaned_df = cleaned_df.sort_values('Date_Cleaned', ascending=False)

    # Export
    cleaned_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Successfully saved {len(cleaned_df)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
