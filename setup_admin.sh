#!/bin/bash

echo "=========================================="
echo "HR System - Admin Setup Script"
echo "=========================================="
echo ""
echo "This will create admin users and fix authentication issues."
echo ""

# Make the script executable
chmod +x "$0"

# Navigate to backend directory
cd backend

# Run the admin setup script
python3 create_admin_simple.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "==========================================" 