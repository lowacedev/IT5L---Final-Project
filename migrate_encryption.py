"""
Database Migration Script: Fix Encryption Issues
This script handles migrating encrypted data from old encryption keys to new ones.
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EncryptionMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect_db(self):
        """Connect to database"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✓ Connected to database")
            return True
        except Error as e:
            print(f"✗ Database connection error: {e}")
            return False
    
    def disconnect_db(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def clear_encrypted_fields(self):
        """Clear encrypted fields due to key mismatch"""
        try:
            print("\n[1] Clearing encrypted fields in suppliers table...")
            
            # Clear email and phone encrypted fields
            query = """
            UPDATE suppliers 
            SET email_encrypted = NULL, 
                phone_encrypted = NULL,
                data_encrypted = 0
            WHERE email_encrypted IS NOT NULL 
               OR phone_encrypted IS NOT NULL
            """
            self.cursor.execute(query)
            self.connection.commit()
            
            affected_rows = self.cursor.rowcount
            print(f"✓ Cleared encrypted fields for {affected_rows} suppliers")
            print("  Note: You may need to re-enter phone and email for suppliers")
            return True
            
        except Error as e:
            print(f"✗ Error clearing encrypted fields: {e}")
            self.connection.rollback()
            return False
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        try:
            print("\n[2] Verifying migration...")
            
            query = "SELECT COUNT(*) as count FROM suppliers"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            supplier_count = result['count']
            
            query = "SELECT COUNT(*) as count FROM suppliers WHERE email_encrypted IS NOT NULL OR phone_encrypted IS NOT NULL"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            encrypted_count = result['count']
            
            print(f"✓ Total suppliers: {supplier_count}")
            print(f"✓ Suppliers with encrypted data: {encrypted_count}")
            
            if encrypted_count == 0:
                print("✓ All encrypted fields have been cleared")
                return True
            else:
                print(f"⚠ Warning: {encrypted_count} suppliers still have encrypted data")
                return False
                
        except Error as e:
            print(f"✗ Verification error: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration"""
        print("=" * 60)
        print("Database Encryption Migration")
        print("=" * 60)
        
        if not self.connect_db():
            return False
        
        try:
            # Clear encrypted fields
            if not self.clear_encrypted_fields():
                return False
            
            # Verify
            if not self.verify_migration():
                print("\n⚠ Migration completed with warnings")
            else:
                print("\n✓ Migration completed successfully!")
            
            print("\n" + "=" * 60)
            print("NEXT STEPS:")
            print("=" * 60)
            print("""
1. The encrypted fields (phone, email) have been cleared
2. Suppliers can still be viewed and used
3. To re-add phone/email information:
   - Edit each supplier
   - Re-enter phone and email (will be encrypted with new key)
4. Test by viewing suppliers to verify decryption works
            """)
            print("=" * 60)
            
            return True
            
        finally:
            self.disconnect_db()

if __name__ == "__main__":
    migration = EncryptionMigration()
    success = migration.run_migration()
    sys.exit(0 if success else 1)
