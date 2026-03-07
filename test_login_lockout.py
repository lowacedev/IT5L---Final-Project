"""
Test login attempt limiting with database persistence
Verifies that lockout survives app restarts
"""
import unittest
import sys
import os
from datetime import datetime, timedelta

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.db import get_db
from app.services.SecureUserService import SecureUserService
from app.security.password_manager import PasswordManager


class TestLoginLockout(unittest.TestCase):
    """Test database-backed login lockout"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.db = get_db()
    
    def setUp(self):
        """Reset test user before each test"""
        cursor = self.db.cursor()
        # Clear test attempts
        cursor.execute("DELETE FROM login_attempts WHERE username = 'lockout_test'")
        cursor.execute("DELETE FROM users WHERE username = 'lockout_test'")
        self.db.commit()
        cursor.close()
        
        # Create test user
        hashed_password = PasswordManager.hash_password("TestPass123!")
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, full_name, role, is_active, failed_login_attempts)
            VALUES (%s, %s, %s, %s, 1, 0)
        """, ('lockout_test', hashed_password, 'Test User', 'cashier'))
        self.db.commit()
        cursor.close()
        
        # Create service instance
        self.service = SecureUserService(self.db)
    
    def tearDown(self):
        """Clean up test data"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM login_attempts WHERE username = 'lockout_test'")
        cursor.execute("DELETE FROM users WHERE username = 'lockout_test'")
        self.db.commit()
        cursor.close()
    
    def test_record_failed_attempts(self):
        """Test recording failed login attempts"""
        # Record 3 failed attempts
        for i in range(3):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Attempt {i+1}")
        
        # Check failed_login_attempts counter
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT failed_login_attempts FROM users WHERE username = %s", ('lockout_test',))
        result = cursor.fetchone()
        cursor.close()
        
        self.assertEqual(result['failed_login_attempts'], 3, "Failed attempts counter should be 3")
        print("✓ Failed attempts recorded to database")
    
    def test_lockout_at_max_attempts(self):
        """Test that account locks after MAX_LOGIN_ATTEMPTS"""
        # Record 5 failed attempts
        for i in range(5):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Attempt {i+1}")
        
        # Check that account is locked
        is_locked = self.service.login_tracker.is_account_locked('lockout_test', max_attempts=5, lockout_minutes=15)
        self.assertTrue(is_locked, "Account should be locked after 5 failed attempts")
        print("✓ Account locked after 5 failed attempts")
    
    def test_cannot_login_when_locked(self):
        """Test that user cannot login when account is locked"""
        # Record 5 failed attempts
        for i in range(5):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Attempt {i+1}")
        
        # Try to login with correct password - should fail due to lockout
        result = self.service.authenticate('lockout_test', 'TestPass123!')
        self.assertIsNone(result, "Authentication should fail when account is locked")
        print("✓ Login rejected when account is locked")
    
    def test_successful_login_resets_counter(self):
        """Test that successful login resets failed_login_attempts counter"""
        # Record 2 failed attempts
        for i in range(2):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Attempt {i+1}")
        
        # Verify counter is 2
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT failed_login_attempts FROM users WHERE username = %s", ('lockout_test',))
        result = cursor.fetchone()
        cursor.close()
        self.assertEqual(result['failed_login_attempts'], 2)
        
        # Login successfully
        user = self.service.authenticate('lockout_test', 'TestPass123!')
        self.assertIsNotNone(user, "Authentication should succeed with correct password")
        
        # Check counter is reset to 0
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT failed_login_attempts FROM users WHERE username = %s", ('lockout_test',))
        result = cursor.fetchone()
        cursor.close()
        self.assertEqual(result['failed_login_attempts'], 0, "Counter should reset to 0 after successful login")
        print("✓ Counter reset to 0 after successful login")
    
    def test_lockout_time_window(self):
        """Test that lockout only counts attempts in the time window"""
        # Record 1 old attempt (20 minutes ago)
        cursor = self.db.cursor()
        old_time = datetime.now() - timedelta(minutes=20)
        cursor.execute("""
            INSERT INTO login_attempts (username, success, reason, attempt_time)
            VALUES (%s, %s, %s, %s)
        """, ('lockout_test', False, "Old attempt", old_time))
        
        # Update failed counter manually
        cursor.execute("UPDATE users SET failed_login_attempts = 1 WHERE username = %s", ('lockout_test',))
        self.db.commit()
        cursor.close()
        
        # Record 4 recent failed attempts
        for i in range(4):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Recent attempt {i+1}")
        
        # Account should be locked (4 recent + 1 old in DB = 5 total, but lockout checks last 15 mins)
        # Actually, the old one is outside the 15 min window, so we have 4 recent ones
        # which should NOT trigger lockout (needs 5)
        failed_count = self.service.login_tracker.get_failed_attempts('lockout_test', minutes=15)
        is_locked = self.service.login_tracker.is_account_locked('lockout_test', max_attempts=5, lockout_minutes=15)
        
        self.assertEqual(failed_count, 4, "Should count only recent attempts within time window")
        self.assertFalse(is_locked, "Should not be locked with only 4 recent attempts")
        print("✓ Lockout time window working correctly (old attempts ignored)")
    
    def test_lockout_survives_app_restart(self):
        """Test that lockout persists in database (simulates app restart)"""
        # Record 5 failed attempts
        for i in range(5):
            self.service.login_tracker.record_attempt('lockout_test', False, reason=f"Attempt {i+1}")
        
        # Simulate app restart by creating a NEW service instance
        new_service = SecureUserService(self.db)
        
        # New instance should still detect the lockout
        is_locked = new_service.login_tracker.is_account_locked('lockout_test', max_attempts=5, lockout_minutes=15)
        self.assertTrue(is_locked, "Lockout should persist after app restart")
        print("✓ Lockout persists across app restart (database-backed)")


if __name__ == '__main__':
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLoginLockout)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
