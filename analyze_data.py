import pandas as pd
import sys

file_path = 'fouk exel com.xlsx'

try:
    # Attempt to read the excel file
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)
    
    print("\n--- Columns ---")
    for col in df.columns:
        print(f"- {col}")
        
    print("\n--- Sample Data (First 3 Rows) ---")
    print(df.head(3).to_string())
    
    print("\n--- Data Info ---")
    df.info()
    
    print("\n--- Missing Values ---")
    print(df.isnull().sum())
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install pandas and openpyxl: pip install pandas openpyxl")
except Exception as e:
    print(f"Error reading file: {e}")
