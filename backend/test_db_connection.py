#!/usr/bin/env python3
"""
DATABASE CONNECTION TESTER
Test different Supabase connection methods
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv
import urllib.parse as urlparse

load_dotenv()

class DatabaseConnectionTester:
    def __init__(self):
        # Get the user's connection string
        self.pooler_url = os.getenv('DATABASE_URL', '')
        
        # Parse the pooler URL to create direct connection URL
        if self.pooler_url:
            parsed = urlparse.urlparse(self.pooler_url)
            # Convert pooler (port 6543) to direct (port 5432)
            direct_host = parsed.hostname.replace('pooler.', '')
            self.direct_url = f"postgresql://{parsed.username}:{parsed.password}@{direct_host}:5432{parsed.path}"
        else:
            self.direct_url = ''

    async def test_connection(self, url, description):
        """Test a specific connection URL"""
        print(f"\n🔄 Testing {description}...")
        print(f"URL: {url[:50]}...")
        
        try:
            # Add SSL requirement
            test_url = url
            if '?' not in test_url:
                test_url += '?sslmode=require'
            elif 'sslmode=' not in test_url:
                test_url += '&sslmode=require'
            
            conn = await asyncpg.connect(
                test_url,
                server_settings={
                    'application_name': 'hr_connection_test'
                }
            )
            
            # Test a simple query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            print(f"✅ {description} - CONNECTION SUCCESSFUL!")
            return True
            
        except Exception as e:
            print(f"❌ {description} - FAILED: {e}")
            return False

    async def test_manual_connection(self, url, description):
        """Test connection using manual parameters"""
        print(f"\n🔄 Testing {description} (Manual Method)...")
        
        try:
            parsed = urlparse.urlparse(url)
            
            conn = await asyncpg.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/'),
                ssl='require',
                server_settings={
                    'application_name': 'hr_connection_test_manual'
                }
            )
            
            # Test a simple query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            print(f"✅ {description} (Manual) - CONNECTION SUCCESSFUL!")
            return True
            
        except Exception as e:
            print(f"❌ {description} (Manual) - FAILED: {e}")
            return False

    async def run_all_tests(self):
        """Run all connection tests"""
        print("🎯 DATABASE CONNECTION TESTER")
        print("=" * 50)
        
        if not self.pooler_url:
            print("❌ No DATABASE_URL found!")
            print("Please set your DATABASE_URL environment variable")
            return
        
        print(f"Original URL: {self.pooler_url}")
        print(f"Direct URL: {self.direct_url}")
        
        successful_methods = []
        
        # Test 1: Direct connection (usually works better)
        if await self.test_connection(self.direct_url, "Direct Connection (Port 5432)"):
            successful_methods.append(("Direct Connection", self.direct_url))
        
        # Test 2: Pooler connection (your original)
        if await self.test_connection(self.pooler_url, "Pooler Connection (Port 6543)"):
            successful_methods.append(("Pooler Connection", self.pooler_url))
        
        # Test 3: Manual direct connection
        if await self.test_manual_connection(self.direct_url, "Direct Connection"):
            successful_methods.append(("Manual Direct Connection", self.direct_url))
        
        # Test 4: Manual pooler connection
        if await self.test_manual_connection(self.pooler_url, "Pooler Connection"):
            successful_methods.append(("Manual Pooler Connection", self.pooler_url))
        
        # Results
        print("\n" + "=" * 50)
        print("📊 CONNECTION TEST RESULTS")
        print("=" * 50)
        
        if successful_methods:
            print("✅ SUCCESSFUL CONNECTION METHODS:")
            for i, (method, url) in enumerate(successful_methods, 1):
                print(f"{i}. {method}")
                print(f"   URL: {url}")
            
            print(f"\n🎯 RECOMMENDED: Use {successful_methods[0][0]}")
            print(f"Set DATABASE_URL to: {successful_methods[0][1]}")
            
        else:
            print("❌ ALL CONNECTION METHODS FAILED!")
            print("\n🔍 TROUBLESHOOTING STEPS:")
            print("1. Check your Supabase project is active")
            print("2. Verify your password is correct")
            print("3. Ensure your IP is whitelisted in Supabase")
            print("4. Try connecting from Supabase dashboard first")
            print("5. Check if database is paused/sleeping")

async def main():
    tester = DatabaseConnectionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 