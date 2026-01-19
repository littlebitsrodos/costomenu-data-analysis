import json
import glob
import os
import sys
import csv
import re
import unicodedata
from datetime import datetime
import pytz
from textblob import TextBlob

# --- Configuration ---
JSON_PATTERN = "crisp_tickets_export_*.json"
OUTPUT_CSV = "categorized_tickets.csv"
TIMEZONE = pytz.timezone('Europe/Athens')

# Category Definitions (Keywords map to Category)
# We use normalized (no accent) Greek for matching.
CATEGORIES = {
    "Error": [
        "error", "bug", "fix", "issue", "problem", "crash", "fail", "wrong", 
        "σφαλμα", "λαθος", "προβλημα", "κολλαει", "δεν λειτουργει", "δεν ανοιγει",
        "buggy", "empty", "blank", "white screen", "κενο", "βγαζει", "δεν αφηνει"
    ],
    "Access": [
        "login", "password", "access", "sign in", "account", "log in", 
        "συνδεση", "κωδικος", "λογαριασμος", "εισοδος", "email", "mail", 
        "confirmation", "verification", "επιβεβαιωση"
    ],
    "Billing": [
        "pricing", "cost", "price", "pay", "payment", "card", "subscription",
        "plan", "invoice", "renew", "offer", "discount", "vat",
        "τιμη", "κοστος", "πληρωμη", "καρτα", "συνδρομη", "πακετο", 
        "τιμολογιο", "ανανεωση", "προσφορα", "φπα"
    ],
    "Units": [
        "unit", "measurement", "kg", "gr", "lit", "piece", "portion", 
        "μοναδα", "μετρησης", "κιλο", "γραμμαρια", "λιτρα", "τεμαχιο", "μεριδα"
    ],
    "Recipe": [
        "recipe", "ingredient", "dish", "menu", "food", "cook",
        "συνταγη", "υλικο", "πιατο", "μενου", "φαγητο", "μαγειρεμα"
    ],
    "Usage": [
        "how", "can i", "print", "export", "import", "excel", "pdf", "download",
        "πως", "μπορω", "εκτυπωση", "εξαγωγη", "εισαγωγη", "κατεβασω", "αποθηκευση"
    ],
    "Greetings": [
        "hello", "hi", "hey", "good morning", "good evening", "test",
        "γεια", "καλημερα", "καλησπερα", "δοκιμη"
    ]
}

# Priority for multi-matches (Topics higher up take precedence)
PRIORITY = ["Error", "Access", "Billing", "Usage", "Recipe", "Units", "Greetings"]

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def load_latest_json():
    files = glob.glob(JSON_PATTERN)
    if not files:
        print("No JSON files found matching pattern:", JSON_PATTERN)
        sys.exit(1)
    latest_file = max(files, key=os.path.getmtime)
    print(f"Loading data from: {latest_file}")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_text(text):
    text_norm = remove_accents(text).lower()
    
    matches = set()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            # Simple substring match
            if kw in text_norm:
                matches.add(category)
                break
    
    # Return based on priority
    for cat in PRIORITY:
        if cat in matches:
            return cat
            
    return "Other"

def calculate_sentiment(text):
    """
    Returns a tuple (Sentiment Label, Polarity Score)
    """
    if not text:
        return "Neutral", 0.0
        
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

def categorize_tickets():
    data = load_latest_json()
    
    results = []
    category_counts = {cat: 0 for cat in PRIORITY}
    category_counts["Other"] = 0
    
    for ticket in data:
        # Get basic info
        created_ms = ticket.get("created_at", 0)
        dt_utc = datetime.fromtimestamp(created_ms / 1000, tz=pytz.utc)
        dt_local = dt_utc.astimezone(TIMEZONE)
        date_str = dt_local.strftime("%Y-%m-%d %H:%M")
        
        meta = ticket.get("meta", {})
        nickname = meta.get("nickname", "Unknown")
        email = meta.get("email", "")
        
        # Determine Category
        messages = ticket.get("messages", [])
        user_messages = [msg for msg in messages if msg.get("from") == "user" and msg.get("type") == "text"]
        
        if not user_messages:
            continue
            
        # Combine all user text for classification context
        full_text = " ".join([msg.get("content", "") for msg in user_messages])
        category = classify_text(full_text)
        
        # Sentiment Analysis
        sentiment, score = calculate_sentiment(full_text)
        
        category_counts[category] += 1
        
        # Get first message for snippet
        first_msg = user_messages[0].get("content", "") if user_messages else ""
        
        # Link to Crisp (Construct URL if possible, otherwise just ID)
        session_id = ticket.get("session_id", "")
        # Assuming standard Crisp URL structure if we knew the Website ID, but session_id is useful enough.
        
        results.append({
            "Date": date_str,
            "Category": category,
            "User": nickname,
            "Email": email,
            "First Message": first_msg,
            "Session ID": session_id,
            "Sentiment": sentiment,
            "Sentiment Score": round(score, 2)
        })
        
    # Sort by Date desc
    results.sort(key=lambda x: x["Date"], reverse=True)
    
    # Export
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Date", "Category", "User", "Email", "First Message", "Session ID", "Sentiment", "Sentiment Score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Categorized {len(results)} tickets.")
    print("\n--- CATEGORY BREAKDOWN ---")
    for cat in PRIORITY + ["Other"]:
        count = category_counts[cat]
        pct = (count / len(results) * 100) if results else 0
        bar = "#" * (int(pct) // 2)
        print(f"{cat:<10} | {count:<4} ({pct:.1f}%) | {bar}")
        
    print(f"\nSaved categorized list to {OUTPUT_CSV}")

if __name__ == "__main__":
    categorize_tickets()
