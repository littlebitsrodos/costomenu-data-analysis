import json
import glob
import os
import re
import csv
from collections import Counter
import sys

import unicodedata

# --- Configuration ---
JSON_PATTERN = "crisp_tickets_export_*.json"
OUTPUT_CSV = "ticket_topics.csv"

# Basic stop words (English + Greek transliterated commonly used in Greek chat)
# Expanding this list iteratively is part of the process.
STOP_WORDS = {
    # English
    "the", "and", "to", "of", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i",
    "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your",
    "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out",
    "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "him", "into", "time", "has", "look", "two",
    "more", "write", "go", "see", "number", "no", "way", "could", "people", "my", "than", "first", "water", "been", "call", "who",
    "oil", "its", "now", "find", "hello", "hi", "hey", "please", "thanks", "thank", "calimera", "kalimera", "geia", "sas",
    "mou", "sou", "kai", "ti", "na", "tha", "to", "me", "einai", "den", "gia", "apo", "alla",
    # Greek (Normalized - no accents) - Latin-ish check
    "kai", "mou", "den", "sas", "tin", "gia", "pou", "sto", "kalisupera", "mia", "stin", "exo", "tis", "pos", "alla", "einai",
    "auto", "auta", "tora", "meta", "edo", "ekei", "ola", "oti", "san", "poly", "poli", "loipon",
    "kalimera", "kalispera", "geia", "euxaristo", "parakalo",
    "o", "i", "to", "ta", "tou", "tis", "tous", "ton", "tin", "oi", "ai",
    "nai", "oxi", "ok", "lipon", "exw", "thelo", "thelw", "mporei", "mporw", "mporo", "prepei", "the", "tha", "na", "me", "mas", "se",
    # Greek Script (Normalized)
    "και", "μου", "δεν", "σας", "την", "για", "που", "στο", "καλησπερα", "ευχαριστω", "μια", "στην", "εχω", "ενα", "απο", "ειναι", "αλλα", 
    "πολυ", "τις", "το", "τα", "ο", "η", "οι", "τον", "τους", "της", "των", "μας", "στον", "στις", "στα", "ειμαι", "οτι", "ολα", "αυτο", 
    "τωρα", "εδω", "εκει", "σαν", "λοιπον", "γεια", "παρακαλω", "ναι", "οχι", "θελω", "μπορω", "πρεπει", "με", "σε", "θα", "να"
}

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def load_latest_json():
    files = glob.glob(JSON_PATTERN)
    if not files:
        print("No JSON files found matching pattern:", JSON_PATTERN)
        sys.exit(1)
    # Sort by modification time, newest first
    latest_file = max(files, key=os.path.getmtime)
    print(f"Loading data from: {latest_file}")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_and_tokenize(text):
    # Lowercase
    text = text.lower()
    # Remove accents
    text = remove_accents(text)
    # Remove special chars/punctuation (keep only alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)
    # Split into words
    tokens = text.split()
    # Remove stop words and short generic words
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return tokens

def get_ngrams(tokens, n=2):
    return zip(*[tokens[i:] for i in range(n)])

def analyze_topics():
    data = load_latest_json()
    
    all_tokens = []
    
    ticket_count = 0
    message_count = 0
    
    for conversation_data in data:
        ticket_count += 1
        messages = conversation_data.get("messages", [])
        
        # Determine who the "user" is (usually not the operator)
        # In Crisp, 'user' type messages come from the visitor/customer.
        user_messages = [msg for msg in messages if msg.get("from") == "user" and msg.get("type") == "text"]
        
        if not user_messages:
            continue
            
        # Strategy: Analyze the FIRST user message to capture the "intent" of the ticket.
        # Alternatively, we could analyze ALL user messages. Let's start with ALL to get a broader cloud.
        # Just creating a giant bag of words for now.
        for msg in user_messages:
            content = msg.get("content", "")
            if content:
                tokens = clean_and_tokenize(content)
                all_tokens.extend(tokens)
                message_count += 1
                
    print(f"Analyzed {ticket_count} tickets.")
    print(f"Processed {message_count} user messages.")
    print(f"Total tokens found: {len(all_tokens)}")
    
    # 1. Frequency Analysis - Unigrams (Single Keywords)
    unigram_counts = Counter(all_tokens)
    
    # 2. Frequency Analysis - Bigrams (Two-word phrases)
    bigram_counts = Counter([" ".join(bg) for bg in get_ngrams(all_tokens, 2)])
    
    # Output Results to Console
    print("\n--- TOP 20 KEYWORDS ---")
    for word, count in unigram_counts.most_common(20):
        print(f"{word}: {count}")
        
    print("\n--- TOP 20 PHRASES ---")
    for phrase, count in bigram_counts.most_common(20):
        print(f"{phrase}: {count}")
        
    # Save to CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Term", "Count"])
        for word, count in unigram_counts.most_common(100):
            writer.writerow(["Keyword", word, count])
        for phrase, count in bigram_counts.most_common(100):
            writer.writerow(["Phrase", phrase, count])
            
    print(f"\nDetailed report saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    analyze_topics()
