"""
Quick test to verify the encryption fix is working
"""

import os
import sys
from dotenv import load_dotenv

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment
load_dotenv()

print("=" * 60)
print("Encryption Fix Verification")
print("=" * 60)

try:
    print("\n[1] Testing encryption module initialization...")
    from app.security.encryption import get_encryption
    
    enc = get_encryption()
    print("✓ Encryption module initialized successfully")
    print(f"  Encryption key loaded from .env: Active")
    
    print("\n[2] Testing encryption/decryption...")
    test_data = "0712345678"
    
    # Test encryption
    encrypted = enc.encrypt(test_data)
    print(f"✓ Encryption successful")
    print(f"  Original: {test_data}")
    print(f"  Encrypted: {encrypted[:50]}...")
    
    # Test decryption
    decrypted = enc.decrypt(encrypted)
    print(f"✓ Decryption successful")
    print(f"  Decrypted: {decrypted}")
    
    # Verify
    if decrypted == test_data:
        print(f"✓ Data integrity verified - original and decrypted match!")
    else:
        print(f"✗ ERROR: Decrypted data doesn't match original!")
        sys.exit(1)
    
    print("\n[3] Testing dict encryption...")
    test_dict = {
        'name': 'Test Supplier',
        'phone': '0712345678',
        'email': 'test@supplier.com'
    }
    
    encrypted_dict = enc.encrypt_dict(test_dict, ['phone', 'email'])
    print(f"✓ Dict encryption successful")
    print(f"  Name (unencrypted): {encrypted_dict['name']}")
    print(f"  Phone (encrypted): {encrypted_dict['phone'][:50]}...")
    print(f"  Email (encrypted): {encrypted_dict['email'][:50]}...")
    
    # Decrypt
    decrypted_dict = enc.decrypt_dict(encrypted_dict, ['phone', 'email'])
    print(f"✓ Dict decryption successful")
    print(f"  Phone (decrypted): {decrypted_dict['phone']}")
    print(f"  Email (decrypted): {decrypted_dict['email']}")
    
    if (decrypted_dict['phone'] == test_dict['phone'] and
        decrypted_dict['email'] == test_dict['email']):
        print(f"✓ Dict data integrity verified!")
    else:
        print(f"✗ ERROR: Dict decrypted data doesn't match!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ ALL ENCRYPTION TESTS PASSED!")
    print("=" * 60)
    print("\n✓ The encryption system is now working correctly!")
    print("✓ You can safely run the application")
    print("✓ Supplier phone/email can now be encrypted and decrypted")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
