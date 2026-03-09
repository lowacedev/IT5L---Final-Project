"""
Password Security Module
Handles password hashing, verification, and validation using bcrypt.
"""

import bcrypt
import re
from app.security.config import SecurityConfig

class PasswordManager:
    """Manages password hashing and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password
            hashed (str): Hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            # Log locally to avoid circular imports
            try:
                from app.utils.logger import get_logger
                logger = get_logger('PASSWORD_CHANGE')
                logger.error(f"Password verification error: {e}")
            except Exception:
                pass
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password against security policy.
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not password:
            return False, "Password cannot be empty"
        
        # Check minimum length
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
        
        # Check for numbers
        if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Check for special characters
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        # Check for uppercase
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_password_complexity(password: str) -> dict:
        """
        Get detailed password complexity information.
        
        Args:
            password (str): Password to check
            
        Returns:
            dict: Complexity metrics
        """
        return {
            'length': len(password),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_numbers': bool(re.search(r'\d', password)),
            'has_special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password)),
        }


# Example usage
if __name__ == "__main__":
    import os
    # Test data with environment variable fallback
    test_password = os.environ.get("TEST_PASSWORD", "SecurePass123")
    
    # Validation example
    is_valid, msg = PasswordManager.validate_password_strength(test_password)
    print(f"Password validation: {is_valid} - {msg}")
    
    # Hash example
    hashed = PasswordManager.hash_password(test_password)
    print(f"Hashed: {hashed[:50]}...")
    
    # Verify
    is_correct = PasswordManager.verify_password(test_password, hashed)
    print(f"Verification: {is_correct}")
    
    # Complexity
    complexity = PasswordManager.validate_password_complexity(test_password)
    print(f"Complexity: {complexity}")
