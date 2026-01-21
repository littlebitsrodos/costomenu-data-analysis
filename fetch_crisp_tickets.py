import os
import json
import time
import argparse
from datetime import datetime, timedelta
from dateutil import parser
from crisp_api import Crisp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PLUGIN_IDENTIFIER = os.getenv("CRISP_PLUGIN_IDENTIFIER")
PLUGIN_KEY = os.getenv("CRISP_PLUGIN_KEY")
WEBSITE_ID = os.getenv("CRISP_WEBSITE_ID")

# Main Database File
DB_FILE = "crisp_full_backup.json"

def get_latest_timestamp(data):
    """Finds the most recent 'updated_at' or 'created_at' in the existing dataset."""
    if not data:
        return None
    
    timestamps = []
    for t in data:
        # Crisp timestamps are usually in milliseconds
        ts = t.get("updated_at") or t.get("created_at")
        if ts:
            timestamps.append(ts)
            
    if timestamps:
        return max(timestamps)
    return None

def main():
    print("--- 🚀 Smart Crisp Ticket Export Agent ---")

    # 1. Parse Arguments
    parser_arg = argparse.ArgumentParser(description="Fetch Crisp conversations incrementally.")
    parser_arg.add_argument("--full", action="store_true", help="Force a full re-fetch of all data.")
    args = parser_arg.parse_args()

    # 2. Check Credentials
    if not all([PLUGIN_IDENTIFIER, PLUGIN_KEY, WEBSITE_ID]):
        print("❌ Error: Missing credentials in .env file.")
        exit(1)

    # 3. Load Existing Data (The "Database")
    known_sessions = {}
    master_data = []
    last_known_ts = 0

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                master_data = json.load(f)
                for t in master_data:
                    known_sessions[t["session_id"]] = t
            
            print(f"📂 Loaded database: {len(master_data)} tickets.")
            last_known_ts = get_latest_timestamp(master_data) or 0
            
            if last_known_ts:
                last_date = datetime.fromtimestamp(last_known_ts / 1000)
                print(f"🕒 Last data point: {last_date}")
        except Exception as e:
            print(f"⚠️ Error reading DB: {e}. Starting fresh.")
    else:
        print("📂 No existing database found. Starting fresh.")

    # Override if --full flag is used
    if args.full:
        print("⚠️ Full fetch requested. Ignoring history.")
        last_known_ts = 0

    # 4. Authenticate
    client = Crisp()
    client.set_tier("plugin")
    client.authenticate(PLUGIN_IDENTIFIER, PLUGIN_KEY)

    # 5. Fetch Loop
    new_tickets = []
    page_number = 1
    has_more = True
    stop_fetching = False

    print(f"🔄 Fetching conversations updated after: {datetime.fromtimestamp(last_known_ts/1000) if last_known_ts else 'The Beginning'}")

    while has_more and not stop_fetching:
        try:
            print(f"  📄 Page {page_number}...", end="\r")
            
            # 20 conversastions per page, usually sorted by updated_at DESC
            conversations = client.website.list_conversations(WEBSITE_ID, page_number)

            if not conversations:
                break

            for conv in conversations:
                session_id = conv["session_id"]
                updated_at = conv.get("updated_at", 0)

                # CHECK: Is this ticket older than our knowledge?
                # If we encounter a ticket that hasn't changed since our last sync, we can theoretically stop.
                # However, Crisp sort order might slightly vary, so let's be safe:
                # We stop if we see a ticket that is significantly older (e.g., 24h older than cut-off) 
                # OR if we hit a known session ID that has the exact same updated_at?
                # Simpler approach for reliability:
                # If updated_at < last_known_ts, we have reached the "old" zone.
                
                if updated_at < last_known_ts and not args.full:
                    # We found a conversation older than our DB's latest state.
                    # Since results are ordered by date, everything subsequent is also old.
                    stop_fetching = True
                    # continue # Don't fetch this one
                    # Actually, let's break strictly.
                    break
                
                # If it's new matching our timeframe OR it's a known ticket that got updated
                if session_id in known_sessions:
                    # Check if it actually changed
                    prev_update = known_sessions[session_id].get("updated_at", 0)
                    if updated_at <= prev_update and not args.full:
                        continue # Skip exact duplicate

                # FETCH DETAILS
                # We only perform the deep fetch (messages) for new/updated sessions
                # print(f"    New/Updated: {session_id}")
                
                ticket_data = {
                    "session_id": session_id,
                    "meta": conv.get("meta", {}),
                    "status": conv.get("status", "unknown"),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                    "active": conv.get("active", {}),
                    "messages": []
                }

                try:
                    msgs = client.website.get_messages_in_conversation(WEBSITE_ID, session_id, {})
                    ticket_data["messages"] = msgs
                    time.sleep(1.0) # Rate limit courtesy
                except Exception as e:
                    print(f"    ⚠️ Failed getting messages for {session_id}: {e}")
                
                new_tickets.append(ticket_data)

            if stop_fetching:
                print(f"\n✅ Reached known data layer (Page {page_number}). Stopping.")
                break

            page_number += 1
            time.sleep(1.0)

        except Exception as e:
            print(f"\n❌ Error on page {page_number}: {e}")
            break

    # 6. Merge & Save
    if new_tickets:
        print(f"\n✨ Found {len(new_tickets)} new/updated tickets.")
        
        # Merge logic: Update master_dict
        for t in new_tickets:
            known_sessions[t["session_id"]] = t # Overwrite with new version
        
        # Convert back to list
        final_list = list(known_sessions.values())
        
        # Sort by updated_at desc
        final_list.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        
        # Atomic Write
        temp_file = DB_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        
        os.replace(temp_file, DB_FILE)
        print(f"💾 Database updated: {DB_FILE}")
    else:
        print("\n💤 No new updates found. Database is up to date.")

if __name__ == "__main__":
    main()
