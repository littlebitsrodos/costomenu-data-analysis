# CostoMenu Data Analytics Dashboard

This repository contains the data processing scripts and the web dashboard for CostoMenu's analytics. It aggregates data from various sources (Viva sales exports, user cohorts, license types) to provide actionable insights into revenue, retention, and customer behavior.

## Features

- **Web Dashboard**: A Flask-based web application (`web_dashboard.py`) visualizing key metrics.
    - **License Analysis**: Breakdown of user license types.
    - **Revenue Trends**: Annual revenue visualization and CAC/LTV analysis.
    - **Retention & Churn**: Cohort analysis and churn risk identification.
- **Data Processing**: Python scripts to clean and enrich raw CSV data.
- **Privacy Focused**: Strict `.gitignore` policy to prevent sensitive customer data from being committed.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/littlebitsrodos/costomenu-data-analysis.git
    cd costomenu-data-analysis
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install flask pandas plotly numpy
    # OR if a requirements.txt exists:
    # pip install -r requirements.txt
    ```

## Usage

### Running the Dashboard
To start the web interface:

```bash
python web_dashboard.py
```

Open your browser and navigate to `http://127.0.0.1:5000`.

### Data Analysis Scripts
Run individual analysis scripts as needed:

```bash
# Example: Run cohort retention analysis
python cohort_retention_analysis.py
```

## Project Structure

- `web_dashboard.py`: Main Flask application entry point.
- `templates/`: HTML templates for the dashboard pages.
- `modules/`: Helper Python modules for specific analysis logic.
- `cohort_retention_analysis.py`: Standalone script for cohort retention logic.
- `schema.sql` / `schema.md`: Database schema documentation.

## Contributing

1.  Ensure no sensitive data (CSV/JSON/SQL) is added to Git.
2.  Follow the existing code style.
3.  Commit changes with clear messages.
