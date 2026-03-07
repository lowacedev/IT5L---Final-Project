#!/usr/bin/env python
"""Test product name validation with forbidden characters"""

from app.security.input_validator import InputValidator

print("=" * 70)
print("TESTING PRODUCT NAME VALIDATION")
print("=" * 70)

# Test cases for product names
test_cases = [
    # (input, should_pass, description)
    ("Intel Core i9", True, "Valid product name"),
    ("AMD Ryzen 5800X", True, "Valid with numbers"),
    ("Kingston 32GB RAM", True, "Valid with multiple words"),
    ("Samsung 860 EVO 1TB", True, "Valid with brand/model"),
    ("Product (OEM)", True, "Valid with parentheses"),
    ("DDR4 2400MHz - Desktop", True, "Valid with hyphen"),
    ("M.2 SSD/NVMe", True, "Valid with slash and period"),
    
    # Invalid cases with forbidden symbols
    ("Intel Core i9!", False, "Contains exclamation mark"),
    ("Product@Name", False, "Contains @ symbol"),
    ("GPU#RTX", False, "Contains hash symbol"),
    ("Price$99", False, "Contains dollar sign"),
    ("50%Off", False, "Contains percent"),
    ("Boost^Performance", False, "Contains caret"),
    ("GPU*Graphics", False, "Contains asterisk"),
    ("Price+Tax", False, "Contains plus sign"),
    ("Data=Info", False, "Contains equals"),
    ("RAM{8GB}", False, "Contains curly braces"),
    ("SSD[512GB]", False, "Contains square brackets"),
    ("Item|Special", False, "Contains pipe"),
    ("Path\\Name", False, "Contains backslash"),
    ("Ratio:1:1", False, "Contains colon"),
    ("List;Item", False, "Contains semicolon"),
    ('Quote"Mark', False, "Contains double quote"),
    ("Single'Quote", False, "Contains single quote"),
    ("Price<$100", False, "Contains less than"),
    ("Price>$50", False, "Contains greater than"),
    ("Question?Mark", False, "Contains question mark"),
    ("Wave~Tilde", False, "Contains tilde"),
    ("Back`Tick", False, "Contains backtick"),
]

print("\n[TEST] Product Name Validation")
print("-" * 70)

passed = 0
failed = 0

for test_input, should_pass, description in test_cases:
    is_valid, message = InputValidator.validate_product_name(test_input)
    
    if is_valid == should_pass:
        status = "PASS"
        passed += 1
        symbol = "✓"
    else:
        status = "FAIL"
        failed += 1
        symbol = "✗"
    
    result = "VALID" if is_valid else "INVALID"
    print(f"{symbol} [{status}] '{test_input}' -> {result}")
    if is_valid != should_pass:
        print(f"       Expected: {'VALID' if should_pass else 'INVALID'}, Got: {result}")
        print(f"       Message: {message}")

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

# Test category validation
print("\n[TEST] Category Validation")
print("-" * 70)

category_tests = [
    ("CPU/Processor", True, "Valid category"),
    ("RAM & Memory", True, "Valid with ampersand"),
    ("SSD-Storage", True, "Valid with hyphen"),
    ("GPU!Graphics", False, "Invalid with exclamation"),
    ("HDD@Storage", False, "Invalid with at symbol"),
]

cat_passed = 0
cat_failed = 0

for test_input, should_pass, description in category_tests:
    is_valid, message = InputValidator.validate_category(test_input)
    
    if is_valid == should_pass:
        status = "PASS"
        cat_passed += 1
        symbol = "✓"
    else:
        status = "FAIL"
        cat_failed += 1
        symbol = "✗"
    
    print(f"{symbol} [{status}] '{test_input}' -> {description}")

print(f"\nCategory Results: {cat_passed} passed, {cat_failed} failed")

# Test brand validation
print("\n[TEST] Brand Validation")
print("-" * 70)

brand_tests = [
    ("Intel", True, "Valid brand"),
    ("AMD", True, "Valid short brand"),
    ("Kingston-HyperX", True, "Valid with hyphen"),
    ("ASUS@ROG", False, "Invalid with at symbol"),
    ("EVGA#Nvidia", False, "Invalid with hash"),
]

brand_passed = 0
brand_failed = 0

for test_input, should_pass, description in brand_tests:
    is_valid, message = InputValidator.validate_brand(test_input)
    
    if is_valid == should_pass:
        status = "PASS"
        brand_passed += 1
        symbol = "✓"
    else:
        status = "FAIL"
        brand_failed += 1
        symbol = "✗"
    
    print(f"{symbol} [{status}] '{test_input}' -> {description}")

print(f"\nBrand Results: {brand_passed} passed, {brand_failed} failed")

# Test model number validation
print("\n[TEST] Model Number Validation")
print("-" * 70)

model_tests = [
    ("RTX 3090", True, "Valid model"),
    ("RTX-3090", True, "Valid model with hyphen"),
    ("RTX-3090-Ti", True, "Valid model with multiple hyphens"),
    ("i9-12900K", True, "Valid model with hyphen"),
    ("RTX@3090", False, "Invalid with at symbol"),
    ("RTX#3090", False, "Invalid with hash"),
]

model_passed = 0
model_failed = 0

for test_input, should_pass, description in model_tests:
    is_valid, message = InputValidator.validate_model_number(test_input)
    
    if is_valid == should_pass:
        status = "PASS"
        model_passed += 1
        symbol = "✓"
    else:
        status = "FAIL"
        model_failed += 1
        symbol = "✗"
    
    print(f"{symbol} [{status}] '{test_input}' -> {description}")

print(f"\nModel Number Results: {model_passed} passed, {model_failed} failed")

# Summary
print("\n" + "=" * 70)
total_passed = passed + cat_passed + brand_passed + model_passed
total_failed = failed + cat_failed + brand_failed + model_failed
print(f"OVERALL: {total_passed} tests passed, {total_failed} tests failed")
print("=" * 70)
