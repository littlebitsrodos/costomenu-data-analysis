import pandas as pd
import json
from pathlib import Path

# Configuration
DROPZONE_DIR = Path("invoices_dropzone")
OUTPUT_FILE = Path("invoices.json")

def process_dropzone():
    """
    Scans the 'invoices_dropzone' folder for files (PDF/Excel) 
    and converts them into a standardized 'invoices.json'.
    
    NOTE: For the MVP, this function MOCKS the OCR/Extraction process 
    by generating synthetic data based on filenames or random logic,
    since we cannot easily run local OCR without heavy dependencies (Tesseract).
    
    In a real production environment, this would import `pypdf` or `openpyxl`.
    """
    
    if not DROPZONE_DIR.exists():
        DROPZONE_DIR.mkdir()
        print(f"📁 Created dropzone at: {DROPZONE_DIR.absolute()}")
        print("Please drop your invoice files here.")
        return

    files = list(DROPZONE_DIR.glob("*.*"))
    if not files:
        print("⚠️ No files found in dropzone.")
        return

    print(f"found {len(files)} files to process...")
    
    processed_data = []
    
    for file_path in files:
        # Mock Processing Logic
        # (This is where the real extraction code will live later)
        print(f"Processing: {file_path.name}")
        
        # Simulated extracted data
        invoice_data = {
            "invoice_number": f"INV-{abs(hash(file_path.name)) % 10000}",
            "date": "2025-01-15",  # Placeholder
            "customer": {
                "name": file_path.stem.replace("_", " ").title(), # Use filename as customer name guess
                "address": "Unknown Address"
            },
            "items": [
                {
                    "description": "Professional License (Annual)",
                    "quantity": 1,
                    "unit_price": 90.00,
                    "total": 90.00
                }
            ],
            "total_amount": 90.00,
            "currency": "EUR"
        }
        processed_data.append(invoice_data)

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Successfully processed {len(processed_data)} invoices into {OUTPUT_FILE}")

if __name__ == "__main__":
    process_dropzone()
