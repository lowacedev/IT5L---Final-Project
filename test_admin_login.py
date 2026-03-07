#!/usr/bin/env python
"""Test admin account and login functionality"""

from app.core.db import get_db
from app.services.SecureUserService import SecureUserService

print("=" * 50)
print("TESTING ADMIN ACCOUNT")
print("=" * 50)

try:
    # Connect to database
    db = get_db()
    print("✓ Database connected")
    
    # Check if admin user exists
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role, is_active FROM users WHERE username = %s", ('admin',))
    admin = cursor.fetchone()
    cursor.close()
    
    if admin:
        print(f"✓ Admin user found: {admin}")
    else:
        print("✗ Admin user NOT found")
        print("\nCreating admin user...")
        service = SecureUserService(db)
        result = service.register_user('admin', 'admin@example.com', 'Admin@123456', 'admin')
        print(f"  Result: {result}")
    
    # Test authentication
    print("\nTesting login...")
    service = SecureUserService(db)
    auth_result = service.authenticate('admin', 'Admin@123456')
    
    if auth_result:
        print(f"✓ LOGIN SUCCESS: {auth_result}")
    else:
        print("✗ LOGIN FAILED")
    
    db.close()
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
