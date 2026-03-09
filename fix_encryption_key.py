"""
Script to fix encryption key issues and migrate encrypted data.
This script generates a proper Fernet key and helps decrypt/re-encrypt data.
"""

from cryptography.fernet import Fernet
import base64
import os
import sys

def generate_fernet_key():
    """Generate a proper Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

def test_key_validity(key_string):
    """Test if a key is a valid Fernet key"""
    try:
        # Try to create a Fernet cipher with this key
        Fernet(key_string.encode() if isinstance(key_string, str) else key_string)
        return True, "Valid Fernet key"
    except Exception as e:
        return False, str(e)

def encrypt_text_with_key(text, key_string):
    """Encrypt text with a given key"""
    try:
        cipher = Fernet(key_string.encode() if isinstance(key_string, str) else key_string)
        encrypted = cipher.encrypt(text.encode())
        return encrypted.decode(), "Success"
    except Exception as e:
        return None, str(e)

def decrypt_text_with_key(encrypted_text, key_string):
    """Decrypt text with a given key"""
    try:
        cipher = Fernet(key_string.encode() if isinstance(key_string, str) else key_string)
        decrypted = cipher.decrypt(encrypted_text.encode())
        return decrypted.decode(), "Success"
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    print("=" * 60)
    print("Encryption Key Generator and Tester")
    print("=" * 60)
    
    # Generate new key
    print("\n[1] Generating new Fernet encryption key...")
    new_key = generate_fernet_key()
    print(f"✓ New Key Generated:\n{new_key}\n")
    
    # Test the new key
    print("[2] Testing new key validity...")
    is_valid, msg = test_key_validity(new_key)
    print(f"{'✓' if is_valid else '✗'} {msg}\n")
    
    # Test encryption/decryption
    print("[3] Testing encryption/decryption...")
    test_data = "0712345678"
    encrypted, enc_msg = encrypt_text_with_key(test_data, new_key)
    if encrypted:
        print(f"✓ Encryption successful: {encrypted}")
        decrypted, dec_msg = decrypt_text_with_key(encrypted, new_key)
        if decrypted:
            print(f"✓ Decryption successful: {decrypted}\n")
        else:
            print(f"✗ Decryption failed: {dec_msg}\n")
    else:
        print(f"✗ Encryption failed: {enc_msg}\n")
    
    # Instructions
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Copy the generated key above
2. Update your .env file:
   - Find the ENCRYPTION_KEY line
   - Replace it with: ENCRYPTION_KEY={new_key}
3. Run the database migration script to re-encrypt existing data:
   python migrate_encryption.py
    """.format(new_key=new_key))
    print("=" * 60)
