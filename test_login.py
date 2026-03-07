#!/usr/bin/env python
"""Test login functionality after logout"""

from app.core.db import get_db
from app.services.SecureUserService import SecureUserService

print("=" * 60)
print("TESTING LOGIN FUNCTIONALITY")
print("=" * 60)

db = get_db()
service = SecureUserService(db)

# Test 1: Admin login
print("\n[TEST 1] Admin Login")
print("-" * 60)
result = service.authenticate('admin', 'Admin@123456')
if result:
    print(f"✓ Admin login successful")
    print(f"  Username: {result['username']}")
    print(f"  Role: {result['role']}")
else:
    print(f"✗ Admin login failed")

# Test 2: Cashier login
print("\n[TEST 2] Cashier Login")
print("-" * 60)
result = service.authenticate('cashier', 'Cashier@123456')
if result:
    print(f"✓ Cashier login successful")
    print(f"  Username: {result['username']}")
    print(f"  Role: {result['role']}")
else:
    print(f"✗ Cashier login failed")

# Test 3: Invalid credentials
print("\n[TEST 3] Invalid Credentials")
print("-" * 60)
result = service.authenticate('admin', 'WrongPassword')
if result is None:
    print(f"✓ Invalid credentials correctly rejected")
else:
    print(f"✗ Invalid credentials were incorrectly accepted")

# Test 4: Multiple sequential logins (simulating logout/login)
print("\n[TEST 4] Sequential Login (Logout/Login Simulation)")
print("-" * 60)
for i in range(3):
    result = service.authenticate('admin', 'Admin@123456')
    if result:
        print(f"  Attempt {i+1}: ✓ Login successful")
    else:
        print(f"  Attempt {i+1}: ✗ Login failed")

db.close()
print("\n" + "=" * 60)
print("LOGIN TESTING COMPLETE")
print("=" * 60)
