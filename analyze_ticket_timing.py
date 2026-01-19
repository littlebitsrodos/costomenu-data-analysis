import json
import glob
import os
import sys
import csv
from collections import Counter
from datetime import datetime
import pytz

# --- Configuration ---
JSON_PATTERN = "crisp_tickets_export_*.json"
OUTPUT_CSV = "ticket_timing.csv"
TIMEZONE = pytz.timezone('Europe/Athens')

def load_latest_json():
    files = glob.glob(JSON_PATTERN)
    if not files:
        print("No JSON files found matching pattern:", JSON_PATTERN)
        sys.exit(1)
    latest_file = max(files, key=os.path.getmtime)
    print(f"Loading data from: {latest_file}")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_timing():
    data = load_latest_json()
    
    hour_counts = Counter()
    day_counts = Counter()
    
    # Day names for sorting
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    ticket_count = 0
    
    for ticket in data: # data is a list
        created_at_ms = ticket.get("created_at")
        if not created_at_ms:
            continue
            
        ticket_count += 1
        
        # Convert ms to seconds
        dt_utc = datetime.fromtimestamp(created_at_ms / 1000, tz=pytz.utc)
        dt_local = dt_utc.astimezone(TIMEZONE)
        
        # Aggregate
        hour_counts[dt_local.hour] += 1
        day_counts[dt_local.strftime("%A")] += 1
        
    print(f"Analyzed {ticket_count} tickets.")
    
    print("\n--- TICKETS BY HOUR OF DAY (Athens Time) ---")
    print(f"{'Hour':<5} | {'Count':<5} | {'Bar'}")
    print("-" * 30)
    sorted_hours = sorted(hour_counts.items())
    # Fill in missing hours with 0
    full_hours = {h: 0 for h in range(24)}
    for h, c in sorted_hours:
        full_hours[h] = c
        
    for h in range(24):
        count = full_hours[h]
        bar = "#" * (count // 2) # Scale down for display
        print(f"{h:02d}:00 | {count:<5} | {bar}")

    print("\n--- TICKETS BY DAY OF WEEK ---")
    print(f"{'Day':<10} | {'Count':<5} | {'Bar'}")
    print("-" * 35)
    
    for day in days_order:
        count = day_counts[day]
        bar = "#" * (count // 2)
        print(f"{day:<10} | {count:<5} | {bar}")
        
    # Export to CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Key", "Count"])
        
        for h in range(24):
            writer.writerow(["HourOfDay", f"{h:02d}:00", full_hours[h]])
            
        for day in days_order:
            writer.writerow(["DayOfWeek", day, day_counts[day]])
            
    print(f"\nTiming data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    analyze_timing()
