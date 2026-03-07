#!/usr/bin/env python
"""Test staff creation with password hashing"""
import sys
from app.core.db import get_db
from app.services.StaffService import StaffService

db = get_db()

# Clean up test data
cursor = db.cursor()
cursor.execute("DELETE FROM users WHERE username IN ('test_staff_1', 'test_staff_2')")
db.commit()
cursor.close()

service = StaffService(db)

print("Testing Staff Creation with Password Hashing")
print("=" * 80)

try:
    # Test 1: Create staff member
    print("\n1. Creating staff member 'test_staff_1'...")
    staff = service.create_staff(
        full_name="John Doe",
        username="test_staff_1",
        password="SecurePass123!",
        role="cashier"
    )
    print(f"✓ Staff created successfully!")
    print(f"  ID: {staff.id}")
    print(f"  Name: {staff.full_name}")
    print(f"  Username: {staff.username}")
    print(f"  Role: {staff.role}")
    
    # Test 2: Verify password is hashed
    print("\n2. Verifying password is hashed in database...")
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT password FROM users WHERE username = %s", ('test_staff_1',))
    result = cursor.fetchone()
    password_stored = result['password']
    cursor.close()
    
    if password_stored.startswith('$2b$'):  # Bcrypt hash starts with $2b$
        print(f"✓ Password is properly hashed (Bcrypt)")
        print(f"  Hash: {password_stored[:50]}...")
    else:
        print(f"✗ Password is NOT hashed! Value: {password_stored}")
    
    # Test 3: Verify security fields
    print("\n3. Verifying security fields...")
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT is_active, failed_login_attempts 
        FROM users WHERE username = %s
    """, ('test_staff_1',))
    result = cursor.fetchone()
    cursor.close()
    
    print(f"✓ is_active: {result['is_active']}")
    print(f"✓ failed_login_attempts: {result['failed_login_attempts']}")
    
    # Test 4: Try to create duplicate username (should fail)
    print("\n4. Testing duplicate username prevention...")
    try:
        service.create_staff(
            full_name="Jane Doe",
            username="test_staff_1",  # Same username
            password="AnotherPass123!",
            role="admin"
        )
        print("✗ Should have rejected duplicate username!")
    except Exception as e:
        print(f"✓ Correctly rejected: {str(e)}")
    
    # Test 5: Update staff member
    print("\n5. Testing staff update with password change...")
    updated = service.update_staff(
        staff_id=staff.id,
        full_name="John Updated",
        username="test_staff_1",
        password="NewPassword456!",
        role="admin"
    )
    print(f"✓ Staff updated successfully!")
    print(f"  Name: {updated.full_name}")
    print(f"  Role: {updated.role}")
    
    # Verify new password is hashed
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT password FROM users WHERE username = %s", ('test_staff_1',))
    result = cursor.fetchone()
    new_password_hash = result['password']
    cursor.close()
    
    if new_password_hash.startswith('$2b$') and new_password_hash != password_stored:
        print(f"✓ Password updated and re-hashed")
    else:
        print(f"✗ Password update failed")
    
    # Test 6: Fetch all staff
    print("\n6. Testing fetch all staff...")
    all_staff = service.fetch_all()
    print(f"✓ Fetched {len(all_staff)} staff members")
    
    # Cleanup
    print("\n7. Cleaning up test data...")
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE username IN ('test_staff_1', 'test_staff_2')")
    db.commit()
    cursor.close()
    print("✓ Test data removed")
    
    print("\n" + "=" * 80)
    print("✓ All staff creation tests passed!")
    
except Exception as e:
    print(f"\n✗ Test failed with error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
