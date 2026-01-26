import pandas as pd
import glob
import os
import warnings
import xlrd

# Suppress warnings
warnings.simplefilter(action='ignore', category=UserWarning)

def execute_query():
    # 1. Find all sales files
    sales_dir = 'Viva - SalesExport'
    pattern = os.path.join(sales_dir, 'SalesExport_*.xls*')
    sales_files = glob.glob(pattern)
    
    if not sales_files:
        print(f"No files found in {sales_dir}")
        return

    print(f"Found {len(sales_files)} sales files.")
    
    all_data = []

    # 2. Iterate and read
    for file in sales_files:
        file_name_short = os.path.basename(file)
        print(f"Reading {file_name_short}...")
        
        df = None
        try:
            # Try reading as Excel first
            if file.lower().endswith('.xls'):
                df = pd.read_excel(file, engine='xlrd')
            else:
                df = pd.read_excel(file)
        except Exception as e_excel:
            # If Excel read fails, try reading as HTML (often exported reports are HTML tables)
            try:
                # Specify decimal and thousands separators for European/Greek format
                dfs = pd.read_html(file, decimal=',', thousands='.')
                if dfs:
                    df = dfs[0] # Assume the main table is the first one or the most relevant
            except Exception as e_html:
                print(f"  Error reading {file_name_short}: Excel error ({e_excel}), HTML error ({e_html})")
                continue

        if df is None:
            continue

        try:
            # Normalize columns
            col_map = {c: c.strip() for c in df.columns}
            df.rename(columns=col_map, inplace=True)
            
            # Identify columns
            date_col = None
            amount_col = None
            
            for c in df.columns:
                c_lower = str(c).lower()
                if c == 'Ημ/νία' or c == 'Ημερομηνία' or 'date' in c_lower:
                    date_col = c
                if c == 'Ποσό' or 'amount' in c_lower or 'total' in c_lower:
                     if c == 'Ποσό':
                        amount_col = c
                     elif amount_col != 'Ποσό' and ('amount' in c_lower or 'total' in c_lower): 
                         if not amount_col: amount_col = c
                        
            if date_col and amount_col:
                clean_df = df[[date_col, amount_col]].copy()
                clean_df.columns = ['date', 'amount']
                all_data.append(clean_df)
            else:
                print(f"  WARNING: Could not find Date/Amount columns in {file_name_short}. Columns: {list(df.columns)}")
                
        except Exception as e:
            print(f"  Error processing {file_name_short}: {e}")

    if not all_data:
        print("No data loaded successfully.")
        return

    # 3. Combine
    full_df = pd.concat(all_data, ignore_index=True)
    
    # 4. Clean Date
    full_df['date'] = pd.to_datetime(full_df['date'], errors='coerce', dayfirst=True)
    full_df = full_df.dropna(subset=['date'])
    full_df['year'] = full_df['date'].dt.year
    
    # 5. Clean Amount
    def clean_currency(x):
        if isinstance(x, str):
            x = x.replace('€', '').strip()
            # Handle European format: 1.234,56 -> 1234.56 or 1234,56 -> 1234.56
            # Assumption: output is consistent. 
            # If '.' appears before ',', likely thousands separator.
            # If only ',' appears, likely decimal.
            # If only '.' appears, could be decimal (US) or thousands (EU). 
            # Given Greek context, assume EU: . is thousands, , is decimal.
            if ',' in x:
                x = x.replace('.', '').replace(',', '.')
            return float(x)
        return x

    full_df['amount'] = full_df['amount'].apply(clean_currency)
    full_df['amount'] = pd.to_numeric(full_df['amount'], errors='coerce')

    # 6. Aggregate
    annual_stats = full_df.groupby('year')['amount'].agg(['sum', 'count']).reset_index()
    annual_stats.columns = ['Year', 'Total Revenue', 'Total Payments']
    annual_stats = annual_stats.sort_values('Year')

    # 7. Print
    pd.options.display.float_format = '{:,.2f}'.format
    print("\n" + "="*50)
    print("REVENUE ANALYSIS BY YEAR")
    print("="*50)
    print(annual_stats.to_string(index=False))
    print("="*50)
    
    grand_total = annual_stats['Total Revenue'].sum()
    print(f"\nGRAND TOTAL REVENUE: €{grand_total:,.2f}")

if __name__ == "__main__":
    execute_query()
