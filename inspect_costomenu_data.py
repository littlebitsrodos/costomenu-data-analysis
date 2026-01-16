import pandas as pd

try:
    # Read without header initially to see the raw layout
    df = pd.read_excel("fouk exel com.xlsx", header=None)
    print("First 10 rows raw:")
    print(df.head(10).to_string())
except Exception as e:
    print(f"Error reading Excel: {e}")
