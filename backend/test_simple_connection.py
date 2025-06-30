#!/usr/bin/env python3
"""
SIMPLE CONNECTION TEST
Test Supabase connection using psycopg2
"""

import psycopg2
import os

def test_connection():
    # Your connection string
    db_url = "postgresql://postgres.udaulvygaczcsrgybdqw:6wjSo5aCUjkCLMHZnp@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"
    
    print("🔄 Testing Supabase connection with psycopg2...")
    print(f"URL: {db_url[:50]}...")
    
    try:
        # Connect
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ CONNECTION SUCCESSFUL!")
        print(f"Database: {result[0][:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")
        return False

if __name__ == "__main__":
    test_connection() 