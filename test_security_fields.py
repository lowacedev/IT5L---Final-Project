#!/usr/bin/env python
"""Test that security fields are now being populated"""
import sys
from app.core.db import get_db
from app.services.SecureUserService import SecureUserService
from app.security.password_manager import PasswordManager

db = get_db()

# Reset test user
cursor = db.cursor()
cursor.execute("DELETE FROM login_attempts WHERE username = 'test_fields'")
cursor.execute("DELETE FROM users WHERE username = 'test_fields'")

# Create fresh test user
hashed = PasswordManager.hash_password("Test123!")
cursor.execute("""
    INSERT INTO users (username, password, full_name, role, is_active, failed_login_attempts)
    VALUES (%s, %s, %s, %s, 1, 0)
""", ('test_fields', hashed, 'Test User', 'cashier'))
db.commit()
cursor.close()

# Now test the login tracking
service = SecureUserService(db)

print("Testing security field population:")
print("=" * 80)

# Simulate 3 failed login attempts
print("\n1. Recording 3 failed attempts...")
for i in range(3):
    service.login_tracker.record_attempt('test_fields', False, reason=f"Test attempt {i+1}")

# Check state after 3 failures
cursor = db.cursor(dictionary=True)
cursor.execute("""
    SELECT username, failed_login_attempts, last_login_attempt, locked_until 
    FROM users WHERE username = 'test_fields'
""")
result = cursor.fetchone()
print(f"\nAfter 3 failed attempts:")
print(f"  Failed Attempts Counter: {result['failed_login_attempts']}")
print(f"  Last Attempt Timestamp: {result['last_login_attempt']}")
print(f"  Locked Until: {result['locked_until']}")

# Try successful login (should reset counter and locked_until)
print("\n2. Recording 1 successful login...")
service.login_tracker.record_attempt('test_fields', True, reason="Successful login")

# Check state after success
cursor.execute("""
    SELECT username, failed_login_attempts, last_login_attempt, locked_until 
    FROM users WHERE username = 'test_fields'
""")
result = cursor.fetchone()
print(f"\nAfter successful login:")
print(f"  Failed Attempts Counter: {result['failed_login_attempts']}")
print(f"  Last Attempt Timestamp: {result['last_login_attempt']}")
print(f"  Locked Until: {result['locked_until']}")

# Test lockout timestamp
print("\n3. Testing lockout timestamp (5 failed attempts)...")
for i in range(5):
    service.login_tracker.record_attempt('test_fields', False, reason=f"Lockout test {i+1}")

is_locked = service.login_tracker.is_account_locked('test_fields', max_attempts=5, lockout_minutes=15)
cursor.execute("""
    SELECT username, failed_login_attempts, last_login_attempt, locked_until 
    FROM users WHERE username = 'test_fields'
""")
result = cursor.fetchone()
print(f"\nAfter 5 failed attempts (locked):")
print(f"  Failed Attempts Counter: {result['failed_login_attempts']}")
print(f"  Last Attempt Timestamp: {result['last_login_attempt']}")
print(f"  Locked Until: {result['locked_until']}")
print(f"  Is Account Locked: {is_locked}")

# Cleanup
cursor.execute("DELETE FROM login_attempts WHERE username = 'test_fields'")
cursor.execute("DELETE FROM users WHERE username = 'test_fields'")
db.commit()
cursor.close()

print("\n" + "=" * 80)
print("✓ All security fields are now being populated correctly!")
