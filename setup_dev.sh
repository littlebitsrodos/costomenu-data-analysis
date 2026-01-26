#!/bin/bash

# CostoMenu Dashboard - Developer Setup Script

echo "🚀 Starting Setup..."

# 1. Create Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 2. Upgrade pip (good practice)
echo "⬆️  Upgrading pip..."
./venv/bin/pip install --upgrade pip

# 3. Install requirements
echo "📥 Installing dependencies from requirements.txt..."
./venv/bin/pip install -r requirements.txt

# 4. Final Instructions
echo ""
echo "🎉 Setup Complete!"
echo "---------------------------------------------------"
echo "To start working, run this command to activate the environment:"
echo ""
echo "    source venv/bin/activate"
echo ""
echo "Then you can run the dashboard with:"
echo "    python web_dashboard.py"
echo "---------------------------------------------------"
