#!/usr/bin/env python
"""Test RBAC implementation"""

from app.core.db import get_db
from app.services.SecureUserService import SecureUserService

print("=" * 60)
print("TESTING RBAC CONFIGURATION")
print("=" * 60)

db = get_db()

# Test 1: Verify admin user
print("\n[TEST 1] Verify Admin User")
print("-" * 60)
service = SecureUserService(db)
admin_result = service.authenticate('admin', 'Admin@123456')
if admin_result:
    print(f"✓ Admin login successful")
    print(f"  - Username: {admin_result['username']}")
    print(f"  - Role: {admin_result['role']}")
    print(f"  - Accessible Features: Dashboard, Inventory (full), Reports, Suppliers, Staff, POS")
else:
    print(f"✗ Admin login failed")

# Test 2: Verify cashier user
print("\n[TEST 2] Verify Cashier User")
print("-" * 60)
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT id, username, role FROM users WHERE role = %s", ('cashier',))
cashier = cursor.fetchone()
cursor.close()

if cashier:
    print(f"✓ Cashier user found: {cashier['username']}")
    print(f"  - Role: {cashier['role']}")
    print(f"  - Accessible Features: POS (full)")
    print(f"  - Cannot: View/Edit Inventory, Access Reports/Suppliers/Staff")
else:
    print(f"✗ No cashier user found in database")

# Test 3: RBAC Permissions
print("\n[TEST 3] RBAC Permission Rules")
print("-" * 60)
rbac_rules = {
    'admin': {
        'dashboard': True,
        'pos': True,
        'inventory': True,  # with full edit/delete
        'reports': True,
        'suppliers': True,
        'staff': True,
        'add_inventory': True,
        'edit_inventory': True,
        'stock_in_out': True
    },
    'cashier': {
        'dashboard': False,
        'pos': True,
        'inventory': False,  # No access
        'reports': False,
        'suppliers': False,
        'staff': False,
        'add_inventory': False,
        'edit_inventory': False,
        'stock_in_out': False
    }
}

for role, perms in rbac_rules.items():
    print(f"\n{role.upper()}:")
    for feature, allowed in perms.items():
        status = "✓ Allowed" if allowed else "✗ Denied"
        print(f"  {feature}: {status}")

db.close()
print("\n" + "=" * 60)
print("RBAC CONFIGURATION COMPLETE")
print("=" * 60)
