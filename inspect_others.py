import pandas as pd

# Load the data
df = pd.read_csv('categorized_tickets.csv')

# Filter for 'Other'
others = df[df['Category'] == 'Other']

# Print sample messages
print(f"Total 'Other' tickets: {len(others)}")
print("-" * 30)
for i, row in others.head(30).iterrows():
    print(f"User: {row['User']}")
    print(f"Msg: {row['First Message']}")
    print("-" * 20)
