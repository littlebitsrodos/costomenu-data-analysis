import json
import glob
import os
import sys
import csv
from datetime import datetime
import pytz
import statistics

# --- Configuration ---
JSON_PATTERN = "crisp_tickets_export_*.json"
OUTPUT_CSV = "response_times.csv"
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

def analyze_response_times():
    data = load_latest_json()
    
    response_times = [] # List of (hour_of_day, minutes_to_respond)
    
    # SLA Thresholds (in minutes)
    SLA_TARGET = 30 # e.g., 30 mins
    
    sla_breaches = 0
    total_responded_tickets = 0
    
    for ticket in data:
        messages = ticket.get("messages", [])
        
        # Sort messages by timestamp just in case
        # Crisp messages usually ordered, but good to be safe if using 'created_at'
        # Check if 'timestamp' or 'created_at' exists in message
        # Based on previous file reads, message struct has 'timestamp' (ms) or parent has it.
        # Let's inspect structure if needed, but assuming standard lists.
        # Actually in recent files we saw list of messages.
        
        # Filter for text messages for simplicity, or just any message?
        # Usually text.
        
        first_user_msg_time = 0
        first_human_response_time = 0
        
        for msg in messages:
            # We want the FIRST user message
            if msg.get("from") == "user" and first_user_msg_time == 0:
                # Use message timestamp if available, else ticket creation?
                # Ticket creation might be slightly before.
                # Let's use message timestamp.
                ts = msg.get("timestamp") # usually in ms
                if ts:
                     first_user_msg_time = ts
            
            # We want the FIRST operator message AFTER the first user message
            if msg.get("from") == "operator" and first_user_msg_time > 0:
                ts = msg.get("timestamp")
                if ts and ts > first_user_msg_time:
                    first_human_response_time = ts
                    break # Found the first response
        
        if first_user_msg_time > 0 and first_human_response_time > 0:
            total_responded_tickets += 1
            
            # Calculate diff in minutes
            diff_ms = first_human_response_time - first_user_msg_time
            diff_mins = diff_ms / 1000 / 60
            
            # Filter out generic outliers (e.g. > 30 days? or just reasonable tickets)
            # Sometimes tickets are merged or crazy. Let's keep reasonable window, e.g., < 7 days (10080 mins)
            if diff_mins < 10080: 
                # Get Hour of Day (Local) for the USER'S message (when the need arose)
                dt_utc = datetime.fromtimestamp(first_user_msg_time / 1000, tz=pytz.utc)
                dt_local = dt_utc.astimezone(TIMEZONE)
                hour = dt_local.hour
                
                response_times.append({
                    "hour": hour,
                    "minutes": diff_mins,
                    "day": dt_local.strftime("%A")
                })
                
                if diff_mins > SLA_TARGET:
                    sla_breaches += 1

    print(f"Analyzed {len(data)} tickets.")
    print(f"Found {len(response_times)} tickets with a first response.")
    
    if not response_times:
        print("No response times calculated.")
        return

    # Metrics
    all_mins = [r["minutes"] for r in response_times]
    avg_response = statistics.mean(all_mins)
    median_response = statistics.median(all_mins)
    
    print(f"\n--- GLOBAL METRICS ---")
    print(f"Average Response Time: {avg_response:.1f} minutes")
    print(f"Median Response Time:  {median_response:.1f} minutes")
    print(f"SLA Breaches (> {SLA_TARGET}m): {sla_breaches} ({sla_breaches/total_responded_tickets*100:.1f}%)")
    
    # Group by Hour
    # We want Avg Response Time per Hour
    hours_data = {h: [] for h in range(24)}
    for r in response_times:
        hours_data[r["hour"]].append(r["minutes"])
        
    print("\n--- RESPONSE TIME BY HOUR (Athens Time) ---")
    print(f"{'Hour':<5} | {'Avg (min)':<10} | {'Median (min)':<12} | {'Count'}")
    print("-" * 50)
    
    csv_rows = []
    
    for h in range(24):
        mins = hours_data[h]
        if mins:
            avg_h = statistics.mean(mins)
            med_h = statistics.median(mins)
            count = len(mins)
        else:
            avg_h = 0
            med_h = 0
            count = 0
            
        # Visual check
        flag = "⚠️" if (h >= 10 and h <= 18 and avg_h > 60) else ""
        
        if count > 0:
            print(f"{h:02d}:00 | {avg_h:<10.1f} | {med_h:<12.1f} | {count:<5} {flag}")
        
        csv_rows.append({
            "Hour": h,
            "AvgResponseMinutes": round(avg_h, 1),
            "MedianResponseMinutes": round(med_h, 1),
            "TicketVolume": count
        })
        
    # Export
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Hour", "AvgResponseMinutes", "MedianResponseMinutes", "TicketVolume"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"\nSaved response time data to {OUTPUT_CSV}")

if __name__ == "__main__":
    analyze_response_times()
