"""
Data Encryption Module
Implements AES encryption for sensitive data.
"""

from cryptography.fernet import Fernet
import base64
import os
from app.security.config import SecurityConfig

class DataEncryption:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self):
        """Initialize encryption with key from config"""
        try:
            # Use the encryption key from config
            key_string = SecurityConfig.ENCRYPTION_KEY
            
            # Convert string key to Fernet-compatible key (32 bytes, base64 encoded)
            if isinstance(key_string, str):
                # Pad or truncate to 32 bytes, then base64 encode
                key_bytes = key_string.encode()[:32]
                key_bytes = key_bytes.ljust(32, b'\0')  # Pad with null bytes if needed
                self.key = base64.urlsafe_b64encode(key_bytes)
            else:
                self.key = key_string
            
            # Create cipher
            self.cipher = Fernet(self.key)
        except Exception as e:
            # Log locally to avoid circular imports
            try:
                from app.utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"Encryption initialization error: {e}")
            except:
                pass
            raise
    
    @staticmethod
    def _get_cipher_from_string(password: str) -> Fernet:
        """
        Derive a cipher from a password string.
        
        Args:
            password (str): Password to derive key from
            
        Returns:
            Fernet: Cipher object
        """
        # Simple key derivation from password
        key_bytes = password.encode()[:32]
        key_bytes = key_bytes.ljust(32, b'\0')
        key = base64.urlsafe_b64encode(key_bytes)
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            str: Encrypted data (base64 encoded)
        """
        try:
            if not isinstance(data, str):
                data = str(data)
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            # Log locally to avoid circular imports
            try:
                from app.utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"Encryption error: {e}")
            except:
                pass
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data (str): Encrypted data to decrypt
            
        Returns:
            str: Decrypted data
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            # Log locally to avoid circular imports
            try:
                from app.utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"Decryption error: {e}")
            except:
                pass
            raise
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data (dict): Dictionary containing data
            fields_to_encrypt (list): List of field names to encrypt
            
        Returns:
            dict: Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data (dict): Dictionary containing encrypted data
            fields_to_decrypt (list): List of field names to decrypt
            
        Returns:
            dict: Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception as e:
                    # Log locally to avoid circular imports
                    try:
                        from app.utils.logger import get_logger
                        logger = get_logger(__name__)
                        logger.warning(f"Could not decrypt field {field}: {e}")
                    except:
                        pass
        return decrypted_data


# Global encryption instance
_encryption = None

def get_encryption() -> DataEncryption:
    """Get or create encryption instance"""
    global _encryption
    if _encryption is None:
        _encryption = DataEncryption()
    return _encryption


# Example usage
if __name__ == "__main__":
    enc = DataEncryption()
    
    # Test basic encryption
    sensitive = "0712345678"  # Phone number
    encrypted = enc.encrypt(sensitive)
    print(f"Original: {sensitive}")
    print(f"Encrypted: {encrypted}")
    decrypted = enc.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test dict encryption
    customer = {
        'name': 'John Doe',
        'phone': '0712345678',
        'email': 'john@example.com'
    }
    
    encrypted_customer = enc.encrypt_dict(customer, ['phone', 'email'])
    print(f"\nEncrypted customer: {encrypted_customer}")
    
    decrypted_customer = enc.decrypt_dict(encrypted_customer, ['phone', 'email'])
    print(f"Decrypted customer: {decrypted_customer}")
