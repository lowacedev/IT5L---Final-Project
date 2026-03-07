"""
Security Test Suite
Comprehensive tests for authentication, authorization, and security features.
"""

import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.security.password_manager import PasswordManager
from app.security.input_validator import InputValidator
from app.security.rbac import (
    get_session_manager,
    RBACManager,
    UserRole,
)
from app.security.encryption import DataEncryption


class TestPasswordSecurity(unittest.TestCase):
    """Test password hashing and validation"""
    
    def test_password_hashing(self):
        """Test bcrypt password hashing"""
        password = "TestPass123!"
        hashed = PasswordManager.hash_password(password)
        
        # Should not be plaintext
        self.assertNotEqual(password, hashed)
        
        # Should start with $2 (bcrypt marker)
        self.assertTrue(hashed.startswith('$2'))
    
    def test_password_verification(self):
        """Test password verification"""
        password = "TestPass123!"
        hashed = PasswordManager.hash_password(password)
        
        # Correct password should verify
        self.assertTrue(PasswordManager.verify_password(password, hashed))
        
        # Wrong password should not verify
        self.assertFalse(PasswordManager.verify_password("WrongPassword", hashed))
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        # Too short
        is_valid, msg = PasswordManager.validate_password_strength("Short1!")
        self.assertFalse(is_valid)
        
        # Missing number
        is_valid, msg = PasswordManager.validate_password_strength("NoNumber!")
        self.assertFalse(is_valid)
        
        # Missing special character
        is_valid, msg = PasswordManager.validate_password_strength("NoSpecial123")
        self.assertFalse(is_valid)
        
        # Missing uppercase
        is_valid, msg = PasswordManager.validate_password_strength("noupppercase123!")
        self.assertFalse(is_valid)
        
        # Valid password
        is_valid, msg = PasswordManager.validate_password_strength("ValidPass123!")
        self.assertTrue(is_valid)
    
    def test_password_complexity_analysis(self):
        """Test password complexity metrics"""
        password = "TestPass123!"
        complexity = PasswordManager.validate_password_complexity(password)
        
        self.assertTrue(complexity['has_lowercase'])
        self.assertTrue(complexity['has_uppercase'])
        self.assertTrue(complexity['has_numbers'])
        self.assertTrue(complexity['has_special'])
        self.assertEqual(complexity['length'], 12)


class TestInputValidation(unittest.TestCase):
    """Test input validation and sanitization"""
    
    def test_username_validation(self):
        """Test username validation"""
        # Valid usernames
        valid_usernames = ['john_doe', 'user123', 'john-doe', 'admin.user']
        for username in valid_usernames:
            is_valid, msg = InputValidator.validate_username(username)
            self.assertTrue(is_valid, f"Should accept: {username}")
        
        # Invalid usernames
        invalid_usernames = ['ab', 'user@domain', 'user name', '']
        for username in invalid_usernames:
            is_valid, msg = InputValidator.validate_username(username)
            self.assertFalse(is_valid, f"Should reject: {username}")
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        valid_emails = ['user@example.com', 'john.doe@domain.co.uk', 'admin+tag@site.org']
        for email in valid_emails:
            is_valid, msg = InputValidator.validate_email(email)
            self.assertTrue(is_valid, f"Should accept: {email}")
        
        # Invalid emails
        invalid_emails = ['notanemail', 'user@', '@example.com', 'user name@example.com']
        for email in invalid_emails:
            is_valid, msg = InputValidator.validate_email(email)
            self.assertFalse(is_valid, f"Should reject: {email}")
    
    def test_numeric_validation(self):
        """Test numeric input validation"""
        # Valid numbers
        is_valid, msg = InputValidator.validate_numeric("123")
        self.assertTrue(is_valid)
        
        is_valid, msg = InputValidator.validate_numeric(45.67)
        self.assertTrue(is_valid)
        
        # With range
        is_valid, msg = InputValidator.validate_numeric("50", min_val=0, max_val=100)
        self.assertTrue(is_valid)
        
        # Out of range
        is_valid, msg = InputValidator.validate_numeric("150", min_val=0, max_val=100)
        self.assertFalse(is_valid)
        
        # Invalid
        is_valid, msg = InputValidator.validate_numeric("abc")
        self.assertFalse(is_valid)
    
    def test_price_validation(self):
        """Test price validation"""
        # Valid prices
        is_valid, msg = InputValidator.validate_price("29.99")
        self.assertTrue(is_valid)
        
        is_valid, msg = InputValidator.validate_price("100")
        self.assertTrue(is_valid)
        
        # Negative price
        is_valid, msg = InputValidator.validate_price("-10")
        self.assertFalse(is_valid)
        
        # Zero price
        is_valid, msg = InputValidator.validate_price("0", allow_zero=False)
        self.assertFalse(is_valid)
    
    def test_quantity_validation(self):
        """Test quantity validation"""
        # Valid quantities
        is_valid, msg = InputValidator.validate_quantity("10")
        self.assertTrue(is_valid)
        
        is_valid, msg = InputValidator.validate_quantity(50)
        self.assertTrue(is_valid)
        
        # Invalid quantities
        is_valid, msg = InputValidator.validate_quantity("0")
        self.assertFalse(is_valid)
        
        is_valid, msg = InputValidator.validate_quantity("-5")
        self.assertFalse(is_valid)
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin' --",
            "1; DELETE FROM users",
            "UNION SELECT * FROM passwords",
        ]
        
        for input_str in dangerous_inputs:
            is_dangerous = InputValidator.check_sql_injection(input_str)
            self.assertTrue(is_dangerous, f"Should detect: {input_str}")
        
        # Safe inputs
        safe_inputs = [
            "John Doe",
            "user@example.com",
            "Product Name",
        ]
        
        for input_str in safe_inputs:
            is_dangerous = InputValidator.check_sql_injection(input_str)
            self.assertFalse(is_dangerous, f"Should accept: {input_str}")


class TestDataEncryption(unittest.TestCase):
    """Test data encryption and decryption"""
    
    def setUp(self):
        """Set up encryption for tests"""
        # Use test encryption key
        import os
        os.environ['ENCRYPTION_KEY'] = 'test_key_32_characters_or_more'
        from app.security.encryption import DataEncryption
        self.enc = DataEncryption()
    
    def test_encrypt_decrypt(self):
        """Test basic encryption/decryption"""
        original = "sensitive data"
        encrypted = self.enc.encrypt(original)
        
        # Encrypted should be different from original
        self.assertNotEqual(original, encrypted)
        
        # Should be able to decrypt
        decrypted = self.enc.decrypt(encrypted)
        self.assertEqual(original, decrypted)
    
    def test_encrypt_dict_fields(self):
        """Test selective field encryption"""
        data = {
            'name': 'John Doe',
            'phone': '1234567890',
            'email': 'john@example.com',
        }
        
        # Encrypt sensitive fields
        encrypted = self.enc.encrypt_dict(data, ['phone', 'email'])
        
        # Name should be unchanged
        self.assertEqual(encrypted['name'], 'John Doe')
        
        # Phone and email should be encrypted
        self.assertNotEqual(encrypted['phone'], data['phone'])
        self.assertNotEqual(encrypted['email'], data['email'])
        
        # Decrypt
        decrypted = self.enc.decrypt_dict(encrypted, ['phone', 'email'])
        self.assertEqual(decrypted['phone'], data['phone'])
        self.assertEqual(decrypted['email'], data['email'])


class TestRBAC(unittest.TestCase):
    """Test Role-Based Access Control"""
    
    def setUp(self):
        """Set up session manager"""
        self.session = get_session_manager()
    
    def test_admin_permissions(self):
        """Test admin role permissions"""
        self.session.start_session(1, 'admin', 'admin')
        
        # Should have all permissions
        self.assertTrue(self.session.can_perform_action('users', 'manage'))
        self.assertTrue(self.session.can_perform_action('logs', 'read'))
        self.assertTrue(self.session.can_perform_action('sales', 'delete'))
        self.assertTrue(self.session.can_access_feature('user_management'))
        self.assertTrue(self.session.can_access_feature('system_logs'))
    
    def test_manager_permissions(self):
        """Test manager role permissions"""
        self.session.start_session(2, 'manager', 'manager')
        
        # Should have limited permissions
        self.assertTrue(self.session.can_perform_action('inventory', 'manage'))
        self.assertTrue(self.session.can_perform_action('sales', 'read_all'))
        
        # Should NOT have
        self.assertFalse(self.session.can_perform_action('logs', 'read'))
        self.assertFalse(self.session.can_perform_action('users', 'manage'))
    
    def test_cashier_permissions(self):
        """Test cashier role permissions"""
        self.session.start_session(3, 'cashier', 'cashier')
        
        # Should have sales access
        self.assertTrue(self.session.can_perform_action('sales', 'create'))
        self.assertTrue(self.session.can_perform_action('inventory', 'read'))
        
        # Should NOT have
        self.assertFalse(self.session.can_perform_action('users', 'manage'))
        self.assertFalse(self.session.can_perform_action('inventory', 'manage'))
        self.assertFalse(self.session.can_access_feature('user_management'))
    
    def test_feature_accessibility(self):
        """Test feature-level access control"""
        # Admin can access all features
        self.session.start_session(1, 'admin', 'admin')
        admin_features = self.session.get_accessible_features()
        self.assertIn('user_management', admin_features)
        self.assertIn('system_logs', admin_features)
        
        # Cashier has limited features
        self.session.end_session()
        self.session.start_session(3, 'cashier', 'cashier')
        cashier_features = self.session.get_accessible_features()
        self.assertNotIn('user_management', cashier_features)
        self.assertNotIn('system_logs', cashier_features)
    
    def test_session_management(self):
        """Test session start and end"""
        # No session initially
        self.assertFalse(self.session.is_authenticated())
        
        # Start session
        self.session.start_session(1, 'testuser', 'admin')
        self.assertTrue(self.session.is_authenticated())
        self.assertEqual(self.session.get_username(), 'testuser')
        
        # End session
        self.session.end_session()
        self.assertFalse(self.session.is_authenticated())
        self.assertIsNone(self.session.get_username())


class TestRBACPermissions(unittest.TestCase):
    """Test RBAC permission checks"""
    
    def test_has_permission(self):
        """Test checking individual permissions"""
        # Admin has manage_users permission
        self.assertTrue(RBACManager.has_permission(UserRole.ADMIN, 'manage_users'))
        
        # Cashier doesn't
        self.assertFalse(RBACManager.has_permission(UserRole.CASHIER, 'manage_users'))
        
        # Cashier has create_sale
        self.assertTrue(RBACManager.has_permission(UserRole.CASHIER, 'create_sale'))
    
    def test_resource_action_check(self):
        """Test resource-level access"""
        # Admin can manage users
        self.assertTrue(RBACManager.has_resource_action(UserRole.ADMIN, 'users', 'manage'))
        
        # Cashier cannot
        self.assertFalse(RBACManager.has_resource_action(UserRole.CASHIER, 'users', 'manage'))
        
        # Both can read inventory
        self.assertTrue(RBACManager.has_resource_action(UserRole.ADMIN, 'inventory', 'read'))
        self.assertTrue(RBACManager.has_resource_action(UserRole.CASHIER, 'inventory', 'read'))


def run_security_tests():
    """Run all security tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestRBAC))
    suite.addTests(loader.loadTestsFromTestCase(TestRBACPermissions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_security_tests()
    sys.exit(0 if success else 1)
