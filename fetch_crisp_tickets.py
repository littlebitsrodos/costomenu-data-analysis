import os
import json
import time
from datetime import datetime
from crisp_api import Crisp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PLUGIN_IDENTIFIER = os.getenv("CRISP_PLUGIN_IDENTIFIER")
PLUGIN_KEY = os.getenv("CRISP_PLUGIN_KEY")
WEBSITE_ID = os.getenv("CRISP_WEBSITE_ID")

# Output filename
OUTPUT_FILE = f"crisp_tickets_export_{datetime.now().strftime('%Y%m%d')}.json"

def main():
    print("--- 🚀 Starting Crisp Ticket Export Agent ---")

    if not all([PLUGIN_IDENTIFIER, PLUGIN_KEY, WEBSITE_ID]):
        print("❌ Error: Missing credentials in .env file.")
        print("Please ensure CRISP_PLUGIN_IDENTIFIER, CRISP_PLUGIN_KEY, and CRISP_WEBSITE_ID are set.")
        exit(1)
    
    # Load existing data to avoid re-fetching detailed messages (Save Quota!)
    existing_tickets = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                for t in old_data:
                    existing_tickets[t["session_id"]] = t
            print(f"ℹ️ Loaded {len(existing_tickets)} existing tickets. Will skip re-fetching their messages.")
        except Exception:
            print("Could not read active file, starting fresh.")

    # 1. Authenticate
    client = Crisp()
    client.set_tier("plugin") 
    client.authenticate(PLUGIN_IDENTIFIER, PLUGIN_KEY)
    
    all_tickets = []
    # If we have a lot of data, maybe we want to search deeper, but let's stick to page 1 start 
    # to catch any new activity too.
    page_number = 1 
    has_more = True

    print(f"🔒 Authenticated as Plugin. Target Website: {WEBSITE_ID}")

    # 2. Iterate through Conversation Pages
    while has_more:
        print(f"📄 Fetching conversation list page {page_number}...")
        
        try:
            # List conversations (20 per page default)
            conversations = client.website.list_conversations(WEBSITE_ID, page_number)
            
            if not conversations:
                print("✅ No more conversations found. Stopping pagination.")
                has_more = False
                break
                
            # 3. Process each conversation
            for conv in conversations:
                session_id = conv["session_id"]
                
                # Check if we already have the FULL ticket (with messages)
                if session_id in existing_tickets and existing_tickets[session_id].get("messages"):
                    # Use cached version
                    # print(f"  ↪️ Skipping {session_id} (Already have it)")
                    all_tickets.append(existing_tickets[session_id])
                    continue
                
                # Metadata for the ticket
                ticket_data = {
                    "session_id": session_id,
                    "meta": conv.get("meta", {}),
                    "status": conv.get("status", "unknown"),
                    "created_at": conv.get("created_at"),
                    "active": conv.get("active", {}),  
                    "messages": [] 
                }
                
                # 4. Deep Fetch: Get messages for this session
                try:
                    messages = client.website.get_messages_in_conversation(WEBSITE_ID, session_id, {})
                    ticket_data["messages"] = messages
                    # Rate limit sleep only when we make a request
                    time.sleep(2.0) 
                except Exception as e:
                    print(f"⚠️ Error fetching messages for {session_id}: {e}")
                    # If rate limited, we should probably stop and save
                    if "429" in str(e) or "quota" in str(e).lower():
                        raise e 
                
                all_tickets.append(ticket_data)
            
            page_number += 1
            # Sleep between pages
            time.sleep(1.0)
            
        except Exception as e:
            print(f"❌ Stop on page {page_number}: {e}")
            break

    # 5. Export to JSON (Portability) with MERGE
    # Create a master dictionary to merge old and new data
    master_db = existing_tickets.copy()
    
    # Update with what we fetched this session
    for t in all_tickets:
        master_db[t["session_id"]] = t
        
    final_output = list(master_db.values())
    
    if final_output:
        print(f"💾 Saving {len(final_output)} tickets to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
        print("--- ✅ Export Complete ---")
        
        # Inspection Helper
        print("\n🔍 Inspection Hint:")
        print("Open the JSON file and look at the 'active' field of a ticket you know the CEO answered.")
        print("This will reveal their 'user_id' or 'nickname' which we can filter by in the future.")
    else:
        print("⚠️ No tickets found.")

if __name__ == "__main__":
    main()
