#!/usr/bin/env python3
"""
CostoMenu Analytics Web Dashboard
Serves analytics pages via localhost web interface with multiple display modes
"""

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

# Configuration
ANALYTICS_DIR = Path(__file__).parent
JSON_FILES = {
    1: "page_01_license_types.json",
    2: "page_02_revenue_analysis.json",
    3: "page_03_renewals_churn.json"
}


@app.route('/')
def index():
    """Home page with navigation to all analytics pages."""
    mode = request.args.get('mode', 'default')
    return render_template('index.html', mode=mode)


@app.route('/page/<int:page_num>')
def page(page_num):
    """Display specific analytics page."""
    if page_num not in JSON_FILES:
        return "Page not found", 404
    
    mode = request.args.get('mode', 'default')
    
    json_file = ANALYTICS_DIR / JSON_FILES[page_num]
    
    if not json_file.exists():
        return f"Data file not found: {json_file}", 404
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return render_template(f'page_{page_num}.html', data=data, mode=mode)


@app.route('/api/page/<int:page_num>')
def api_page(page_num):
    """API endpoint for raw JSON data."""
    if page_num not in JSON_FILES:
        return jsonify({"error": "Page not found"}), 404
    
    json_file = ANALYTICS_DIR / JSON_FILES[page_num]
    
    if not json_file.exists():
        return jsonify({"error": "Data file not found"}), 404
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return jsonify(data)


if __name__ == '__main__':
    print("=" * 80)
    print("🌐 CostoMenu Analytics Dashboard")
    print("=" * 80)
    print()
    print("Starting server...")
    print()
    print("📊 Dashboard URLs:")
    print("  • Default Mode:  http://localhost:5000")
    print("  • Brand Mode:    http://localhost:5000?mode=brand")
    print("  • Dark Mode:     http://localhost:5000?mode=dark")
    print()
    print("Available pages:")
    print("  • Page 1:  http://localhost:5000/page/1  (License Types)")
    print("  • Page 1 (Brand):  http://localhost:5000/page/1?mode=brand")
    print("  • Page 1 (Dark):   http://localhost:5000/page/1?mode=dark")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
