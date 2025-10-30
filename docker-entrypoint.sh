#!/bin/bash
set -e

echo "🚀 Starting Driverless Container..."
echo ""

# Run the C++ pipeline to generate initial results
echo "📊 Running pipeline to generate initial results..."
./build/driverless
echo ""

# Start the web server
echo "🌐 Starting web server on http://0.0.0.0:8080"
echo "   Container ready!"
echo ""
export SERVER_HOST=0.0.0.0
exec python3 server.py
