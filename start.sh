#!/bin/bash

# Start script for Driverless Results Viewer

echo "🚀 Starting Driverless Results Viewer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r requirements.txt

# Start the server
echo "🌐 Starting server on http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""
python3 server.py
