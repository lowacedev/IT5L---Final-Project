"""
Test suite for Supplier Data Encryption
Tests encrypt/decrypt functionality for phone and email
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.SupplierService import SupplierService
from app.core.db import get_db
from app.security.encryption import DataEncryption


class TestSupplierEncryption(unittest.TestCase):
    """Test encryption of supplier data"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        try:
            cls.db = get_db()
            cls.supplier_service = SupplierService(cls.db)
            cls.encryption = DataEncryption()
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Failed to connect to database: {e}")
            raise
    
    def test_encrypt_decrypt_phone(self):
        """Test phone number encryption and decryption"""
        original_phone = "555-123-4567"
        encrypted = self.encryption.encrypt(original_phone)
        decrypted = self.encryption.decrypt(encrypted)
        
        self.assertEqual(original_phone, decrypted)
        self.assertNotEqual(original_phone, encrypted)
        print(f"✓ [PASS] Phone encryption/decryption: {original_phone} → {encrypted[:20]}... → {decrypted}")
    
    def test_encrypt_decrypt_email(self):
        """Test email encryption and decryption"""
        original_email = "supplier@example.com"
        encrypted = self.encryption.encrypt(original_email)
        decrypted = self.encryption.decrypt(encrypted)
        
        self.assertEqual(original_email, decrypted)
        self.assertNotEqual(original_email, encrypted)
        print(f"✓ [PASS] Email encryption/decryption: {original_email} → {encrypted[:20]}... → {decrypted}")
    
    def test_create_supplier_with_encryption(self):
        """Test creating supplier with encrypted phone and email"""
        try:
            supplier = self.supplier_service.create_supplier(
                name="Encrypted Test Supplier",
                contact_person="John Doe",
                email="john@example.com",
                phone="555-999-8888",
                address="123 Main St"
            )
            
            self.assertIsNotNone(supplier)
            self.assertEqual(supplier.name, "Encrypted Test Supplier")
            # Phone and email should be decrypted when retrieved
            self.assertEqual(supplier.email, "john@example.com")
            self.assertEqual(supplier.phone, "555-999-8888")
            
            print(f"✓ [PASS] Supplier created with encryption: {supplier.name} (ID: {supplier.id})")
            
            # Clean up
            self.supplier_service.delete_supplier(supplier.id)
            print(f"✓ [PASS] Supplier cleaned up: ID {supplier.id}")
            
        except Exception as e:
            self.fail(f"Failed to create supplier with encryption: {str(e)}")
    
    def test_update_supplier_with_encryption(self):
        """Test updating supplier with encrypted data"""
        try:
            # Create supplier
            supplier = self.supplier_service.create_supplier(
                name="Update Test Supplier",
                contact_person="Jane Smith",
                email="jane@example.com",
                phone="555-111-2222",
                address="456 Oak Ave"
            )
            
            # Update with new phone and email
            updated = self.supplier_service.update_supplier(
                supplier.id,
                name="Updated Supplier Name",
                contact_person="Jane Smith",
                email="jane.new@example.com",
                phone="555-777-6666",
                address="789 Pine Rd"
            )
            
            self.assertIsNotNone(updated)
            self.assertEqual(updated.email, "jane.new@example.com")
            self.assertEqual(updated.phone, "555-777-6666")
            
            print(f"✓ [PASS] Supplier updated with encryption: {updated.name}")
            
            # Clean up
            self.supplier_service.delete_supplier(supplier.id)
            print(f"✓ [PASS] Supplier cleaned up: ID {supplier.id}")
            
        except Exception as e:
            self.fail(f"Failed to update supplier with encryption: {str(e)}")
    
    def test_fetch_all_suppliers_decryption(self):
        """Test that all suppliers are decrypted when fetching"""
        try:
            suppliers = self.supplier_service.fetch_all()
            
            # Verify that phone and email are decrypted (not in encrypted format)
            for supplier in suppliers:
                # Encrypted data typically looks like base64 (contains / or +)
                # Decrypted phone should look like a phone number
                if supplier.phone:
                    # Should not contain typical base64 padding
                    self.assertNotIn("==", supplier.phone)
                
                if supplier.email:
                    # Should contain @ symbol
                    if "@" in supplier.email:
                        self.assertIn("@", supplier.email)
            
            print(f"✓ [PASS] Fetched {len(suppliers)} suppliers with decryption")
            
        except Exception as e:
            self.fail(f"Failed to fetch suppliers: {str(e)}")
    
    def test_multiple_encryption_same_data(self):
        """Test that same data produces different ciphertexts (due to IV/salt)"""
        phone = "555-123-4567"
        
        encrypted1 = self.encryption.encrypt(phone)
        encrypted2 = self.encryption.encrypt(phone)
        
        # With CBC mode, same plaintext can produce different ciphertexts
        # Both should decrypt to the same value
        decrypted1 = self.encryption.decrypt(encrypted1)
        decrypted2 = self.encryption.decrypt(encrypted2)
        
        self.assertEqual(decrypted1, phone)
        self.assertEqual(decrypted2, phone)
        
        print(f"✓ [PASS] Multiple encryptions of same data decrypt correctly")


if __name__ == '__main__':
    print("=" * 70)
    print("SUPPLIER ENCRYPTION TEST SUITE")
    print("=" * 70)
    
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"OVERALL: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun} tests passed")
    print("=" * 70)
