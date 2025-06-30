#!/usr/bin/env python3
"""
Dedicated startup script for the HR Dashboard backend
This avoids conflicts with other main.py files in the Python environment
"""

import os
import sys
import uvicorn

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Starting HR Dashboard Backend Server...")
    print("📁 Backend directory:", backend_dir)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 