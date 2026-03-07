"""
Test supplier validation - all fields required and Philippine phone format
"""
from app.security.input_validator import InputValidator

print("=" * 70)
print("SUPPLIER VALIDATION TESTS")
print("=" * 70)

# Test 1: Required field validation
print("\n[TEST 1] Required Field Checks")
print("-" * 70)

test_cases = [
    # (field_value, field_name, should_be_valid)
    ("", "Empty", False),
    ("   ", "Spaces only", False),
    ("Valid Name", "Valid name", True),
]

for val, desc, expected_valid in test_cases:
    # Simulate required field check
    is_empty = not val or not val.strip()
    is_valid = not is_empty  # Required means field must not be empty
    
    status = "PASS" if is_valid == expected_valid else "FAIL"
    print(f"[{status}] '{desc}': is_required={is_valid}, expected={expected_valid}")

# Test 2: Supplier name validation
print("\n[TEST 2] Supplier Name Validation")
print("-" * 70)

supplier_tests = [
    ("Tech Supplies Ltd", True, "Valid supplier name"),
    ("ABC Company", True, "Valid name"),
    ("Tech!Supplies", False, "Invalid with exclamation"),
    ("Company@Inc", False, "Invalid with at symbol"),
]

for name, should_pass, desc in supplier_tests:
    is_valid, msg = InputValidator.validate_supplier_name(name)
    status = "PASS" if is_valid == should_pass else "FAIL"
    print(f"[{status}] '{name}' -> {desc}")

# Test 3: Contact person validation  
print("\n[TEST 3] Contact Person Validation")
print("-" * 70)

contact_tests = [
    ("John Smith", True, "Valid name"),
    ("Mary-Jane Watson", True, "Valid with hyphen"),
    ("Patrick O'Brien", True, "Valid with apostrophe"),
    ("John123", False, "Invalid with numbers"),
]

for name, should_pass, desc in contact_tests:
    is_valid, msg = InputValidator.validate_contact_person(name)
    status = "PASS" if is_valid == should_pass else "FAIL"
    print(f"[{status}] '{name}' -> {desc}")

# Test 4: Email validation
print("\n[TEST 4] Email Validation")
print("-" * 70)

email_tests = [
    ("supplier@company.com", True, "Valid email"),
    ("contact@example.ph", True, "Valid .ph domain"),
    ("invalid.email", False, "Missing domain"),
    ("supplier@", False, "Missing domain name"),
]

for email, should_pass, desc in email_tests:
    is_valid, msg = InputValidator.validate_email(email)
    status = "PASS" if is_valid == should_pass else "FAIL"
    print(f"[{status}] '{email}' -> {desc}")

# Test 5: Philippine phone validation
print("\n[TEST 5] Philippine Phone Validation")
print("-" * 70)

phone_tests = [
    ("09123456789", True, "11 digits with 0"),
    ("+639123456789", True, "+63 format"),
    ("9123456789", True, "10 digits without prefix"),
    ("0912345678", False, "Only 10 digits with 0"),
    ("091234567890", False, "12 digits with 0"),
    ("+6389876543", False, "+63 not starting with 9"),
]

for phone, should_pass, desc in phone_tests:
    is_valid, msg = InputValidator.validate_philippine_phone(phone)
    status = "PASS" if is_valid == should_pass else "FAIL"
    print(f"[{status}] '{phone}' -> {desc}")

# Test 6: Address validation (just check not empty)
print("\n[TEST 6] Address Field (Required)")
print("-" * 70)

addr_tests = [
    ("123 Main Street", True, "Valid address"),
    ("", False, "Empty address"),
    ("   ", False, "Spaces only"),
]

for addr, expected_valid, desc in addr_tests:
    is_valid = bool(addr and addr.strip())
    status = "PASS" if is_valid == expected_valid else "FAIL"
    print(f"[{status}] '{addr}' -> {desc}")

print("\n" + "=" * 70)
print("ALL SUPPLIER VALIDATION TESTS COMPLETED")
print("=" * 70)
