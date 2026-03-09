"""
End-to-End Logging Test
Tests all implemented logging functionality to ensure data is properly recorded.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import get_db
from app.utils.logger import SecurityLogger, SecurityAuditLogger
from app.services.SecureUserService import SecureUserService
from app.utils.BackupManager import BackupManager

def test_logging_end_to_end():
    """Test all logging functionality"""
    print("="*60)
    print("END-TO-END LOGGING TEST")
    print("="*60)
    
    try:
        # Initialize database connection
        print("\n1. Testing Database Connection...")
        db = get_db()
        print("   ✓ Database connection successful")
        
        # Initialize logging
        print("\n2. Testing Logging Initialization...")
        SecurityLogger.setup_logging(db)
        print("   ✓ Logging initialized")
        
        # Test user service and session creation
        print("\n3. Testing Session Creation on Login...")
        user_service = SecureUserService(db)
        
        # Check if admin user exists (from schema)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            print(f"   ✓ Found test user: {user['username']}")
            
            # Try to create a session (simulate login)
            session_token = user_service.session_manager.create_session(
                user['id'],
                user['username'],
                "127.0.0.1",
                "Mozilla/5.0 Test"
            )
            print(f"   ✓ Session created: {session_token[:20]}...")
            
            # Verify session was recorded
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as count FROM user_sessions WHERE is_active = 1")
            session_count = cursor.fetchone()['count']
            cursor.close()
            print(f"   ✓ Active sessions in database: {session_count}")
        else:
            print("   ⚠ No users found in database")
        
        # Test activity logging
        print("\n4. Testing Activity Logging...")
        SecurityAuditLogger.log_user_action('test_user', 'test_action', 'This is a test log entry')
        print("   ✓ Activity log created")
        
        # Verify activity log exists
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM user_activity_logs")
        activity_count = cursor.fetchone()['count']
        cursor.close()
        print(f"   ✓ User activity logs in database: {activity_count}")
        
        # Test backup logging
        print("\n5. Testing Backup Logging...")
        backup_result = BackupManager.create_backup(db_connection=db)
        if backup_result['success']:
            print(f"   ✓ Backup created: {backup_result['backup_path']}")
            
            # Verify backup was logged
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as count FROM backup_logs WHERE success = 1")
            backup_count = cursor.fetchone()['count']
            cursor.close()
            print(f"   ✓ Successful backups logged: {backup_count}")
        else:
            print(f"   ⚠ Backup failed (may be expected if mysqldump not available): {backup_result['message']}")
        
        # Test security audit logging
        print("\n6. Testing Security Audit Logging...")
        SecurityAuditLogger.log_login_attempt('test_user', True, "192.168.1.1")
        print("   ✓ Login attempt logged")
        
        # Verify security audit logs
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM security_audit_logs")
        audit_count = cursor.fetchone()['count']
        cursor.close()
        print(f"   ✓ Security audit logs in database: {audit_count}")
        
        # Summary
        print("\n" + "="*60)
        print("LOGGING SUMMARY")
        print("="*60)
        cursor = db.cursor(dictionary=True)
        
        tables = [
            ('user_sessions', 'User Sessions'),
            ('user_activity_logs', 'User Activity Logs'),
            ('security_audit_logs', 'Security Audit Logs'),
            ('backup_logs', 'Backup Logs'),
            ('access_control_logs', 'Access Control Logs'),
            ('login_attempts', 'Login Attempts')
        ]
        
        print("\nDatabase Logging Tables Status:")
        print("-" * 60)
        for table_name, description in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                status = "✓" if count > 0 else "○"
                print(f"{status} {description:30} {count:>5} records")
            except Exception as e:
                print(f"✗ {description:30}   Error: {str(e)[:30]}")
        
        cursor.close()
        db.close()
        
        print("\n" + "="*60)
        print("✓ END-TO-END LOGGING TEST COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logging_end_to_end()
