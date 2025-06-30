#!/usr/bin/env python3
"""
Simple script to create admin users using raw SQL
This bypasses SQLAlchemy relationship issues
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import SessionLocal, engine
from auth import get_password_hash
from datetime import datetime
import uuid

def create_admin_users_sql():
    """Create admin users using raw SQL"""
    
    try:
        print("🚀 Setting up admin users with SQL...")
        
        # Get database connection
        connection = engine.connect()
        
        # Create admin accounts
        admin_accounts = [
            {
                'email': 'superadmin@company.com',
                'password': 'SuperAdmin123!',
                'role': 'admin',
                'settings': '{"is_super_admin": true}',
                'description': 'SUPER ADMIN (Full Access)'
            },
            {
                'email': 'demo@company.com',
                'password': 'Demo123!',
                'role': 'admin',
                'settings': '{"is_demo_admin": true}',
                'description': 'DEMO ADMIN (Full Access)'
            },
            {
                'email': 'hradmin@company.com',
                'password': 'HRAdmin123!',
                'role': 'hr_admin',
                'settings': '{"is_hr_admin": true}',
                'description': 'HR ADMIN (HR Operations)'
            }
        ]
        
        created_accounts = []
        
        for account in admin_accounts:
            # Check if user already exists
            from sqlalchemy import text
            result = connection.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": account['email']}
            )
            
            if result.fetchone():
                # Update existing user
                hashed_password = get_password_hash(account['password'])
                connection.execute(
                    text("""UPDATE users 
                       SET hashed_password = :password, role = :role, is_active = true, 
                           profile_settings = :settings, updated_at = :updated_at 
                       WHERE email = :email"""),
                    {
                        "password": hashed_password, 
                        "role": account['role'], 
                        "settings": account['settings'], 
                        "updated_at": datetime.utcnow(), 
                        "email": account['email']
                    }
                )
                print(f"✅ Updated {account['description']}: {account['email']}")
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                hashed_password = get_password_hash(account['password'])
                connection.execute(
                    text("""INSERT INTO users (id, email, hashed_password, role, is_active, 
                                        profile_settings, created_at, updated_at) 
                       VALUES (:id, :email, :password, :role, :active, :settings, :created_at, :updated_at)"""),
                    {
                        "id": user_id,
                        "email": account['email'],
                        "password": hashed_password,
                        "role": account['role'],
                        "active": True,
                        "settings": account['settings'],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                print(f"✅ Created {account['description']}: {account['email']}")
            
            created_accounts.append(account)
        
        # Fix existing users without passwords
        print("🔧 Fixing existing users without passwords...")
        
        # Get users without passwords
        result = connection.execute(
            text("SELECT id, email FROM users WHERE hashed_password IS NULL")
        )
        
        users_without_passwords = result.fetchall()
        fixed_users = []
        
        for user in users_without_passwords:
            email_prefix = user[1].split('@')[0]  # user[1] is email, user[0] is id
            default_password = f"{email_prefix.capitalize()}123!"
            hashed_password = get_password_hash(default_password)
            
            connection.execute(
                text("""UPDATE users 
                   SET hashed_password = :password, is_active = true, updated_at = :updated_at 
                   WHERE id = :id"""),
                {
                    "password": hashed_password,
                    "updated_at": datetime.utcnow(),
                    "id": user[0]  # user[0] is id
                }
            )
            
            fixed_users.append({
                'email': user[1],  # user[1] is email
                'password': default_password
            })
            print(f"🔑 Fixed password for: {user[1]}")
        
        # Commit all changes
        connection.commit()
        
        print("\n✅ ADMIN SETUP COMPLETE!")
        print("=" * 50)
        print("🔑 LOGIN CREDENTIALS:")
        print("=" * 50)
        
        for account in created_accounts:
            print(f"{account['description']}:")
            print(f"  Email: {account['email']}")
            print(f"  Password: {account['password']}")
            print(f"  Role: {account['role']}")
            print()
        
        if fixed_users:
            print("🔑 FIXED USER PASSWORDS:")
            print("=" * 30)
            for user in fixed_users:
                print(f"  {user['email']} → {user['password']}")
        
        print("\n🎉 You can now log in with any of these accounts!")
        print("💡 The SUPER ADMIN can access everything in the system.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin users: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, 'orig'):
            print(f"Original error: {e.orig}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return False

if __name__ == "__main__":
    print("🚀 HR System Admin Setup (Simple)")
    print("=" * 40)
    
    if create_admin_users_sql():
        print("\n🎉 Setup completed successfully!")
        print("🌐 Start your backend server and log in with the credentials above.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1) 