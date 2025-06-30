#!/usr/bin/env python3
"""
SUPABASE CONNECTION FIXER
Generate correct connection URLs for your Supabase database
"""

import asyncio
import asyncpg
import urllib.parse as urlparse

# Your original connection string
original_url = "postgresql://postgres.udaulvygaczcsrgybdqw:6wjSo5aCUjkCLMHZnp@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

def generate_connection_urls(original):
    """Generate different Supabase connection URL variations"""
    parsed = urlparse.urlparse(original)
    
    # Extract components
    username = parsed.username
    password = parsed.password
    hostname = parsed.hostname
    database = parsed.path.lstrip('/')
    
    # Generate different URL variations
    urls = {}
    
    # 1. Session pooler (pgbouncer) - transaction mode
    urls["Session Pooler"] = f"postgresql://{username}:{password}@{hostname}:6543/{database}?sslmode=require&pgbouncer=true"
    
    # 2. Direct connection - extract project ref from hostname
    if 'pooler.supabase.com' in hostname:
        # Extract region and create direct URL
        region = hostname.split('.')[0].replace('aws-0-', '')
        # The project ref should be in your username after the dot
        project_ref = username.split('.')[1] if '.' in username else username
        direct_host = f"db.{project_ref}.supabase.co"
        urls["Direct Connection"] = f"postgresql://{username}:{password}@{direct_host}:5432/{database}?sslmode=require"
    
    # 3. Alternative pooler format
    urls["Alt Pooler"] = f"postgresql://{username}:{password}@{hostname}:6543/{database}?sslmode=require&pool_mode=transaction"
    
    # 4. Session mode pooler
    urls["Session Mode"] = f"postgresql://{username}:{password}@{hostname}:6543/{database}?sslmode=require&pool_mode=session"
    
    return urls

async def test_connection_url(url, name):
    """Test a specific connection URL"""
    print(f"\n🔄 Testing {name}...")
    
    try:
        conn = await asyncpg.connect(
            url,
            server_settings={
                'application_name': 'supabase_connection_test'
            }
        )
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        await conn.close()
        
        print(f"✅ {name} - SUCCESS!")
        print(f"   Database: {result[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ {name} - FAILED: {str(e)[:100]}...")
        return False

async def main():
    print("🔧 SUPABASE CONNECTION FIXER")
    print("=" * 50)
    print(f"Original URL: {original_url}")
    
    urls = generate_connection_urls(original_url)
    
    print(f"\n📋 Generated {len(urls)} connection variations:")
    for name, url in urls.items():
        print(f"  {name}: {url[:60]}...")
    
    print(f"\n🧪 Testing connections...")
    
    working_urls = []
    
    for name, url in urls.items():
        if await test_connection_url(url, name):
            working_urls.append((name, url))
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if working_urls:
        print("✅ WORKING CONNECTION(S) FOUND!")
        for i, (name, url) in enumerate(working_urls, 1):
            print(f"\n{i}. {name}")
            print(f"   URL: {url}")
        
        print(f"\n🎯 RECOMMENDED URL TO USE:")
        print(f"{working_urls[0][1]}")
        
        print(f"\n💡 SET THIS IN YOUR ENVIRONMENT:")
        print(f'$env:DATABASE_URL="{working_urls[0][1]}"')
        
    else:
        print("❌ NO WORKING CONNECTIONS FOUND!")
        print("\n🔍 Please check:")
        print("1. Is your Supabase project active?")
        print("2. Is the password correct?")
        print("3. Is your IP address whitelisted?")
        print("4. Try connecting via Supabase dashboard first")

if __name__ == "__main__":
    asyncio.run(main()) 