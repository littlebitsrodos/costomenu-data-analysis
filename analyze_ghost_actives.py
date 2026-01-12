import pandas as pd

# Load data
try:
    df = pd.read_csv('cleaned_costo_menu.csv')
    
    # Filter conditions
    # 1. License status is ACTIVE (assuming case insensitive check just in case, though file has ACTIVE)
    # 2. Last activity date is NaN
    # 3. ExpirationDate is NaN
    # 4. License is 'Beginner' or 'Professional'
    
    # Ensure columns exist
    required_cols = ['License status', 'Last activity date', 'ExpirationDate', 'License', 'Fullname', 'Email', 'Company']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        exit()
        
    df['Last activity date'] = pd.to_datetime(df['Last activity date'], dayfirst=True, errors='coerce')
    df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], dayfirst=True, errors='coerce')
    
    criterion = (
        (df['License status'].str.upper() == 'ACTIVE') &
        (df['Last activity date'].isna()) &
        (df['ExpirationDate'].isna()) &
        (df['License'].isin(['Beginner', 'Professional']))
    )
    
    ghost_actives = df[criterion]
    
    print(f"Found {len(ghost_actives)} users matching criteria.")
    print("-" * 30)
    
    if not ghost_actives.empty:
        # Show top 20 breakdown
        print(ghost_actives[['Fullname', 'Email', 'Company', 'License']].head(20).to_string(index=False))
        
        print("\nBreakdown by License:")
        print(ghost_actives['License'].value_counts())
        
except Exception as e:
    print(f"Error: {e}")
