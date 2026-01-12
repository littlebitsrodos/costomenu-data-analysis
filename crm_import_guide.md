# CRM Import Guide for Costo.menu Data

## Overview
This guide explains how to import the cleaned customer data (`cleaned_costo_menu.csv`) into a CRM system (e.g., HubSpot or Zoho CRM). It covers:
- Required field mapping between the CSV columns and CRM fields.
- Preparing the CSV for import (encoding, date format).
- Step‑by‑step import process for HubSpot (Free tier) and Zoho CRM (Free tier).
- Post‑import validation checklist.

---

## 1. CSV Preparation
1. **Encoding**: Ensure the file is saved as UTF‑8 without BOM. Most spreadsheet programs (Excel, Google Sheets) export with this encoding by default.
2. **Date Formats**: Dates should be in `YYYY‑MM‑DD` (ISO) format. The cleaning script already converts dates to this format.
3. **Missing Values**: The script replaces missing values with placeholder strings (`"N/A"` for phone, `"Unknown"` for company, etc.). These will be imported as empty fields if the CRM treats them as blanks.
4. **Column Order**: The order does not matter as long as the header row matches the field names in the mapping table below.

---

## 2. Field Mapping
| CSV Column | CRM Field (HubSpot) | CRM Field (Zoho) | Description |
|------------|--------------------|-----------------|-------------|
| `User ID` | `Contact ID` (custom) | `Contact ID` (custom) | Unique identifier from the source system |
| `Full Name` | `Full Name` | `Full Name` | Customer's full name |
| `Email` | `Email` | `Email` | Primary email address |
| `Phone` | `Phone` | `Phone` | Phone number (may be `N/A`)
| `Company` | `Company` | `Company` | Company name (`Unknown` if missing)
| `License Type` | `License Type` (custom) | `License Type` (custom) | e.g., `Professional`, `Free`
| `License Expiration` | `License Expiration` (custom) | `License Expiration` (custom) | Date when the license expires |
| `License Status` | `License Status` (custom) | `License Status` (custom) | e.g., `Active`, `Expired`
| `Last Activity` | `Last Activity Date` (custom) | `Last Activity Date` (custom) | Date of last platform activity |
| `Recipe Count` | `Recipe Count` (custom) | `Recipe Count` (custom) | Number of recipes created |
| `Ingredients Count` | `Ingredients Count` (custom) | `Ingredients Count` (custom) | Number of ingredients used |
| `Menus Count` | `Menus Count` (custom) | `Menus Count` (custom) | Number of menus created |
| `Distributors Count` | `Distributors Count` (custom) | `Distributors Count` (custom) | Number of distributors linked |
| `Registration Date` | `Registration Date` (custom) | `Registration Date` (custom) | Date the user registered |
| `Total Payments` | `Total Payments` (custom) | `Total Payments` (custom) | Sum of all payments made |
| `Days Since Last Activity` | `Days Since Last Activity` (custom) | `Days Since Last Activity` (custom) | Calculated metric |
| `Customer Lifetime Value` | `Customer LTV` (custom) | `Customer LTV` (custom) | Calculated metric |

---

## 3. Import Steps – HubSpot (Free Tier)
1. Log in to HubSpot and navigate to **Contacts → Contacts**.
2. Click **Import** → **Start an import** → **File from computer**.
3. Choose **One file** → **One object (Contacts)**.
4. Upload `cleaned_costo_menu.csv`.
5. In the **Map columns** screen, HubSpot will auto‑match columns. Review each mapping and use the table above to map any custom fields that HubSpot did not detect.
6. Click **Finish import**.
7. After the import completes, go to **Contacts → Contacts** and verify that the number of records matches the CSV row count (≈ 4 200).

---

## 4. Import Steps – Zoho CRM (Free Tier)
1. Log in to Zoho CRM and go to **Setup → Data Administration → Import**.
2. Choose **Leads** (or **Contacts**, depending on your data model).
3. Upload `cleaned_costo_menu.csv`.
4. In the **Field Mapping** step, select **Auto‑Map** and then manually adjust any fields that were not matched using the mapping table.
5. Click **Next** and confirm the import.
6. Once finished, check **Leads → All Leads** to confirm the record count.

---

## 5. Post‑Import Validation Checklist
- [ ] Record count matches the CSV row count.
- [ ] Dates appear in the correct format.
- [ ] No `N/A` or `Unknown` values appear in required fields (e.g., Email, Full Name).
- [ ] Custom fields (License Type, LTV, etc.) contain data.
- [ ] Run a quick filter in the CRM to verify that **Active** licenses (`License Status = "Active"`) are correctly imported.
- [ ] Verify that the calculated fields (`Days Since Last Activity`, `Customer LTV`) are numeric and not empty.

---

## 6. Next Steps
- Set up **CRM dashboards** using the fields above to monitor the KPIs described in the implementation plan.
- Schedule a **weekly sync** to refresh the CSV (run `clean_and_analyze.py`) and re‑import incremental updates.
- Consider automating the import with the CRM’s API for a fully automated pipeline.

---

*Prepared by Antigravity – Advanced Agentic Coding*
