"""
Test Philippine phone number validation
"""
from app.security.input_validator import InputValidator

print("=" * 70)
print("TESTING PHILIPPINE PHONE NUMBER VALIDATION")
print("=" * 70)

test_cases = [
    # Valid cases
    ("09123456789", True, "Valid 11-digit with 0 prefix"),
    ("09198765432", True, "Valid 11-digit with 0 prefix"),
    ("+639123456789", True, "Valid +63 format"),
    ("+639198765432", True, "Valid +63 format"),
    ("9123456789", True, "Valid 10-digit without prefix"),
    ("09123456789 ext 123", True, "Valid with formatting"),
    ("09123456789", True, "Valid format"),
    ("(09) 123-456-789", True, "Valid with parentheses and dashes"),
    
    # Invalid cases
    ("0912345678", False, "Too short (10 digits with 0)"),
    ("091234567891", False, "Too long (12 digits with 0)"),
    ("+6301234567", False, "+63 with 0 prefix is invalid"),
    ("+6389876543", False, "+63 not starting with 9"),
    ("8912345678", False, "10 digits but starts with 8"),
    ("+63812345678", False, "+63 starting with 8"),
    ("", False, "Empty string"),
    ("abcdefghijk", False, "Letters only"),
    ("0912-34-5678", False, "Invalid format"),
    ("+1234567890", False, "Non-Philippine country code"),
]

passed = 0
failed = 0

print("\n[TEST] Philippine Phone Number Validation")
print("-" * 70)

for phone, should_pass, description in test_cases:
    is_valid, msg = InputValidator.validate_philippine_phone(phone)
    
    if is_valid == should_pass:
        status = "✓ [PASS]"
        passed += 1
    else:
        status = "✗ [FAIL]"
        failed += 1
    
    result = "Valid" if is_valid else "Invalid"
    expected = "Valid" if should_pass else "Invalid"
    print(f"{status} '{phone}' -> {result} ({description})")

print("\n" + "=" * 70)
print(f"OVERALL: {passed}/{len(test_cases)} tests passed")
print("=" * 70)
