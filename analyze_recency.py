import pandas as pd
from datetime import datetime

# Load data
try:
    df = pd.read_csv('cleaned_costo_menu.csv')
    
    # Parse date
    df['Last activity date'] = pd.to_datetime(df['Last activity date'], dayfirst=True, errors='coerce')
    
    # Calculate recency
    now = datetime.now()
    df['Recency'] = (now - df['Last activity date']).dt.days
    
    # Segments
    active = df[df['Recency'] <= 30].shape[0]
    at_risk = df[(df['Recency'] > 30) & (df['Recency'] <= 90)].shape[0]
    dormant = df[df['Recency'] > 90].shape[0]
    unknown = df['Recency'].isna().sum()
    
    total = len(df)
    
    print(f"Total Users: {total}")
    print(f"🟢 Active (<=30d): {active} ({active/total*100:.1f}%)")
    print(f"🟡 At Risk (31-90d): {at_risk} ({at_risk/total*100:.1f}%)")
    print(f"🔴 Dormant (>90d): {dormant} ({dormant/total*100:.1f}%)")
    print(f"⚪ Unknown (No Date): {unknown} ({unknown/total*100:.1f}%)")
    
except Exception as e:
    print(f"Error: {e}")
