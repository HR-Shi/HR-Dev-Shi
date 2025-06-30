#!/bin/bash

echo "🎯 HR Dashboard - Synthetic Data Generator"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip install -r requirements_synthetic.txt

echo ""
echo "🚀 Starting synthetic data generation..."
echo ""

# Run the synthetic data generator
python3 generate_synthetic_data.py

echo ""
echo "✅ Data generation completed!"
echo "You can now access your HR Dashboard with realistic data" 