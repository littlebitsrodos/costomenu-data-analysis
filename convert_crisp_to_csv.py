import json
import csv
import os
from datetime import datetime

# Configuration
INPUT_FILE = "crisp_tickets_export_20260119.json"
OUTPUT_FILE = f"ceo_tickets_summary_{datetime.now().strftime('%Y%m%d')}.csv"
CEO_USER_ID = "4325c4cb-80cf-43c8-96a4-35cae2fe0100"

def format_timestamp(ts_ms):
    if not ts_ms:
        return ""
    # Crisp uses milliseconds
    return datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

def main():
    print(f"📂 Reading from {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        tickets = json.load(f)

    print(f"📊 Processing {len(tickets)} tickets...")
    
    csv_rows = []
    
    for ticket in tickets:
        messages = ticket.get("messages", [])
        
        # Check if CEO participated in this ticket
        ceo_messages = [m for m in messages if m.get("user", {}).get("user_id") == CEO_USER_ID]
        
        # If we only want tickets answered by CEO, uncomment the next two lines:
        if not ceo_messages:
           continue

        # Basic Info
        session_id = ticket.get("session_id")
        meta = ticket.get("meta", {})
        customer_nickname = meta.get("nickname", "Unknown")
        customer_email = meta.get("email", "")
        customer_phone = meta.get("phone", "")
        created_at = format_timestamp(ticket.get("created_at"))
        
        # Transcript construction
        transcript_lines = []
        last_user_msg = ""
        last_ceo_msg = ""
        
        for msg in messages:
            sender = "Unknown"
            content = msg.get("content", "")
            msg_type = msg.get("type", "")
            
            # Skip system messages like 'event' if needed, mostly text is relevant
            if msg_type != "text":
                continue

            if msg.get("from") == "user":
                sender = "Customer"
                last_user_msg = content 
            elif msg.get("from") == "operator":
                user_id = msg.get("user", {}).get("user_id")
                nickname = msg.get("user", {}).get("nickname", "Agent")
                if user_id == CEO_USER_ID:
                    sender = "CEO (Costo)"
                    last_ceo_msg = content
                else:
                    sender = f"Agent ({nickname})"
            
            transcript_lines.append(f"[{sender}]: {content}")
            
        full_transcript = "\n".join(transcript_lines)

        csv_rows.append({
            "Session ID": session_id,
            "Date": created_at,
            "Customer Name": customer_nickname,
            "Customer Email": customer_email,
            "Status": "Resolved" if ticket.get("status") == 0 else "Pending/Open", # 1 is usually unresolved/open
            "CEO Participated": "Yes" if ceo_messages else "No",
            "Last Customer Question": last_user_msg,
            "Last CEO Response": last_ceo_msg,
            "Full Transcript": full_transcript
        })

    # Sort by date (newest first)
    csv_rows.sort(key=lambda x: x["Date"], reverse=True)

    print(f"💾 Saving {len(csv_rows)} relevant tickets to CSV...")
    
    if csv_rows:
        headers = csv_rows[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"✅ Successfully created {OUTPUT_FILE}")
    else:
        print("⚠️ No relevant tickets found matching criteria.")

if __name__ == "__main__":
    main()
