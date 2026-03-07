#!/usr/bin/env python
"""Test validation for suppliers and staff"""

from app.security.input_validator import InputValidator

print("=" * 70)
print("TESTING SUPPLIER AND STAFF VALIDATION")
print("=" * 70)

# Test Supplier Name Validation
print("\n[TEST] Supplier Name Validation")
print("-" * 70)

supplier_tests = [
    ("Tech Supplies Ltd", True, "Valid supplier name"),
    ("ABC Trading Company", True, "Valid long supplier name"),
    ("Hardware & Parts Co.", True, "Valid with ampersand"),
    ("Tech!Supplies", False, "Invalid with exclamation"),
    ("ABC@Trading", False, "Invalid with at symbol"),
    ("Parts#Inc", False, "Invalid with hash"),
]

supplier_passed = 0
for test_input, should_pass, description in supplier_tests:
    is_valid, msg = InputValidator.validate_supplier_name(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        supplier_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nSupplier Tests: {supplier_passed}/{len(supplier_tests)} passed")

# Test Contact Person Validation
print("\n[TEST] Contact Person Validation")
print("-" * 70)

contact_tests = [
    ("John Smith", True, "Valid contact name"),
    ("Mary-Jane Watson", True, "Valid name with hyphen"),
    ("Patrick O'Brien", True, "Valid name with apostrophe"),
    ("John123", False, "Invalid with numbers"),
    ("John@Smith", False, "Invalid with at symbol"),
    ("Contact!", False, "Invalid with exclamation"),
]

contact_passed = 0
for test_input, should_pass, description in contact_tests:
    is_valid, msg = InputValidator.validate_contact_person(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        contact_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nContact Person Tests: {contact_passed}/{len(contact_tests)} passed")

# Test Full Name Validation (Staff)
print("\n[TEST] Staff Full Name Validation")
print("-" * 70)

fullname_tests = [
    ("Alice Johnson", True, "Valid staff name"),
    ("Robert Smith-Brown", True, "Valid name with hyphen"),
    ("Sean O'Malley", True, "Valid name with apostrophe"),
    ("Alice123", False, "Invalid with numbers"),
    ("Alice@Jones", False, "Invalid with at symbol"),
    ("Staff!", False, "Invalid with exclamation"),
    ("Bob#Wilson", False, "Invalid with hash"),
]

fullname_passed = 0
for test_input, should_pass, description in fullname_tests:
    is_valid, msg = InputValidator.validate_full_name(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        fullname_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nFull Name Tests: {fullname_passed}/{len(fullname_tests)} passed")

# Test Role Validation
print("\n[TEST] Staff Role Validation")
print("-" * 70)

role_tests = [
    ("admin", True, "Valid admin role"),
    ("cashier", True, "Valid cashier role"),
    ("manager", True, "Valid manager role"),
    ("ADMIN", True, "Valid admin role (uppercase)"),
    ("user", False, "Invalid user role"),
    ("superadmin", False, "Invalid superadmin role"),
    ("", False, "Empty role"),
]

role_passed = 0
for test_input, should_pass, description in role_tests:
    is_valid, msg = InputValidator.validate_role(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        role_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nRole Tests: {role_passed}/{len(role_tests)} passed")

# Test Username Validation
print("\n[TEST] Username Validation")
print("-" * 70)

username_tests = [
    ("john_doe", True, "Valid username"),
    ("alice.smith", True, "Valid username with dot"),
    ("bob-johnson", True, "Valid username with hyphen"),
    ("user123", True, "Valid username with numbers"),
    ("user@name", False, "Invalid with at symbol"),
    ("user!", False, "Invalid with exclamation"),
    ("ab", False, "Too short"),
    ("at", False, "Too short"),
]

username_passed = 0
for test_input, should_pass, description in username_tests:
    is_valid, msg = InputValidator.validate_username(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        username_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nUsername Tests: {username_passed}/{len(username_tests)} passed")

# Test Phone Validation
print("\n[TEST] Phone Number Validation")
print("-" * 70)

phone_tests = [
    ("555-123-4567", True, "Valid US phone"),
    ("555.123.4567", True, "Valid phone with dots"),
    ("(555) 123-4567", True, "Valid phone with parentheses"),
    ("5551234567", True, "Valid phone without formatting"),
    ("555123", False, "Too short"),
    ("abc-123-4567", False, "Contains letters"),
]

phone_passed = 0
for test_input, should_pass, description in phone_tests:
    is_valid, msg = InputValidator.validate_phone(test_input)
    if is_valid == should_pass:
        print(f"✓ [PASS] '{test_input}' -> {description}")
        phone_passed += 1
    else:
        print(f"✗ [FAIL] '{test_input}' -> Expected {'VALID' if should_pass else 'INVALID'}")

print(f"\nPhone Tests: {phone_passed}/{len(phone_tests)} passed")

# Summary
print("\n" + "=" * 70)
total_tests = (len(supplier_tests) + len(contact_tests) + len(fullname_tests) + 
               len(role_tests) + len(username_tests) + len(phone_tests))
total_passed = supplier_passed + contact_passed + fullname_passed + role_passed + username_passed + phone_passed
print(f"OVERALL: {total_passed}/{total_tests} tests passed")
print("=" * 70)
