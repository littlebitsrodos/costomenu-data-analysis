import imaplib
import email
import os
import sys
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
EMAIL = os.getenv("GMAIL_USER")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
ATTACHMENT_DIR = Path("invoices_dump")

def clean_filename(filename):
    """Sanitize filename to avoid filesystem issues."""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()

def fetch_invoices():
    if not EMAIL or not PASSWORD:
        print("❌ Error: Missing credentials.")
        print("Please set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file.")
        print("Note: You must use a Google 'App Password' if 2FA is enabled.")
        return

    # Create directory
    ATTACHMENT_DIR.mkdir(exist_ok=True)
    
    print(f"🔌 Connecting to {IMAP_SERVER} as {EMAIL}...")
    
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        
        # Select mailbox
        mail.select("inbox")
        
        # Search for emails
        # Broad search: Subject contains "Invoice" or "Timologio" (Greek)
        print("🔍 Searching for emails with 'Invoice' or 'Τιμολόγιο' in subject...")
        status, messages = mail.search(None, '(OR SUBJECT "Invoice" SUBJECT "Τιμολόγιο")')
        
        if status != "OK":
            print("❌ Search failed.")
            return
            
        email_ids = messages[0].split()
        print(f" found {len(email_ids)} emails. Processing...")
        
        count = 0
        for e_id in email_ids:
            # Fetch the email
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Walk through the email parts
                    for part in msg.walk():
                        if part.get_content_maintype() == "multipart":
                            continue
                        if part.get("Content-Disposition") is None:
                            continue
                            
                        filename = part.get_filename()
                        if filename:
                            # Decode filename
                            fname, fencoding = decode_header(filename)[0]
                            if isinstance(fname, bytes):
                                filename = fname.decode(fencoding if fencoding else "utf-8")
                                
                            # Filter for likely invoice formats
                            if filename.lower().endswith((".pdf", ".xlsx", ".xls", ".csv")):
                                filepath = ATTACHMENT_DIR / clean_filename(filename)
                                
                                # Don't overwrite if exists (optional logic)
                                if not filepath.exists():
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    print(f"   ⬇️ Downloaded: {filename} (from: {subject})")
                                    count += 1
                                else:
                                    print(f"   ⏭️ Skipped (Exists): {filename}")

        print("\n" + "="*30)
        print(f"✅ Comparison Complete.")
        print(f"📥 Total attachments downloaded: {count}")
        print(f"pj📂 Location: {ATTACHMENT_DIR.absolute()}")
        print("="*30)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    fetch_invoices()
