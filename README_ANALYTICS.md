# CostoMenu Database Analytics

A multi-page analytics system for analyzing CostoMenu user data, license types, retention patterns, and business metrics.

## 📊 Available Analytics Pages

### Page 1: License Type Distribution
**File:** `page_01_license_types.py`  
**SQL Query:** `SELECT license_type, COUNT(*) as total_users FROM users GROUP BY license_type`

Analyzes the distribution of users across different license types (Beginner, Expert, Professional) with:
- Total user counts per license type
- Percentage distribution
- Detailed breakdown by license status (ACTIVE/EXPIRED)
- Expiration rate analysis
- JSON export for dashboard integration

**Run:**
```bash
python3 page_01_license_types.py
```

**Output:** Console display + `page_01_license_types.json`

---

### Page 2: [Coming Soon] Cohort Retention Analysis
Analyze user retention patterns by registration cohort.

### Page 3: [Coming Soon] User Activity Patterns
Track user engagement and activity metrics.

---

## 🗂️ Data Sources

- **UserSummary_1769434497556.csv** - Main user data export
- **Dump20250902.sql** - Full database dump (if needed)

---

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install pandas numpy
   ```

2. **Run any analytics page:**
   ```bash
   python3 page_01_license_types.py
   ```

3. **View JSON output:**
   ```bash
   cat page_01_license_types.json
   ```

---

## 📝 Adding New Analytics Pages

To add a new analytics page, follow this structure:

1. **Create file:** `page_XX_descriptive_name.py` (use sequential numbering)

2. **Include header:**
   ```python
   """
   ═══════════════════════════════════════════════════════════════════════════════
   📊 COSTOMENU DATABASE ANALYTICS - PAGE X: [TITLE]
   ═══════════════════════════════════════════════════════════════════════════════
   
   SQL Query Equivalent:
       [Your SQL query here]
   
   Purpose:
       [Brief description]
   
   Navigation:
       • Page 1: License Type Distribution
       • Page X: [Your Page] (YOU ARE HERE)
       
   Last Updated: YYYY-MM-DD
   ═══════════════════════════════════════════════════════════════════════════════
   """
   ```

3. **Export JSON:**
   ```python
   OUTPUT_JSON = Path(__file__).parent / "page_XX_name.json"
   
   export_data = {
       "page": X,
       "title": "Your Title",
       "analysis_date": datetime.now().isoformat(),
       # ... your data
   }
   
   with open(OUTPUT_JSON, 'w') as f:
       json.dump(export_data, f, indent=2)
   ```

4. **Update this README** with the new page information

---

## 🎯 Design Principles

1. **One Page = One Analysis** - Each page focuses on a specific analytical question
2. **SQL-First Thinking** - Document the equivalent SQL query for clarity
3. **Consistent Formatting** - Use box-drawing characters for professional output
4. **JSON Export** - All pages export structured data for dashboard integration
5. **Self-Documenting** - Include purpose, navigation, and last updated date

---

## 📂 File Organization

```
data-analytics-dashboard/
├── page_01_license_types.py          # Page 1: License analysis
├── page_01_license_types.json        # Page 1 output
├── page_02_*.py                       # Future pages...
├── UserSummary_1769434497556.csv     # Source data
├── README_ANALYTICS.md                # This file
└── requirements.txt                   # Python dependencies
```

---

## 🔍 Data Integrity

- **Source Data:** All analytics read from `UserSummary_1769434497556.csv`
- **No Mutations:** Analytics scripts never modify source data
- **Reproducible:** Same input always produces same output
- **Timestamped:** All JSON exports include analysis timestamp

---

## 💡 Tips

- Run analytics pages in sequence to build a complete picture
- JSON outputs can be consumed by dashboards or other tools
- Each page is standalone - no dependencies between pages
- Use `grep` to quickly find specific analyses: `grep -l "cohort" page_*.py`

---

**Last Updated:** 2026-01-26  
**Maintained By:** CostoMenu Analytics Team
