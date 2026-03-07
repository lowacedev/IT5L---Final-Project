"""
Test suite for CAPTCHA Generator functionality
"""

import unittest
import os
import tempfile
from app.utils.CaptchaGenerator import CaptchaGenerator


class TestCaptchaGenerator(unittest.TestCase):
    """Test cases for CAPTCHA generation and validation"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.captcha = CaptchaGenerator()
        self.temp_dir = tempfile.gettempdir()
    
    def test_generate_code_length(self):
        """Test CAPTCHA code has correct length"""
        code = self.captcha.generate_code(length=6)
        self.assertEqual(len(code), 6)
        print(f"✓ [PASS] Generated code length: {len(code)}")
    
    def test_generate_code_custom_length(self):
        """Test CAPTCHA code with custom length"""
        code = self.captcha.generate_code(length=8)
        self.assertEqual(len(code), 8)
        print(f"✓ [PASS] Custom length code: {code}")
    
    def test_generate_code_no_confusing_chars(self):
        """Test CAPTCHA code excludes confusing characters"""
        for _ in range(10):
            code = self.captcha.generate_code()
            # Should not contain 0, 1, O, or I
            self.assertNotIn('0', code)
            self.assertNotIn('1', code)
            self.assertNotIn('O', code)
            self.assertNotIn('I', code)
        print("✓ [PASS] No confusing characters in codes")
    
    def test_generate_code_alphanumeric(self):
        """Test CAPTCHA code contains only alphanumeric characters"""
        for _ in range(10):
            code = self.captcha.generate_code()
            self.assertTrue(code.isalnum())
        print("✓ [PASS] Codes are alphanumeric")
    
    def test_generate_image(self):
        """Test CAPTCHA image generation"""
        image = self.captcha.generate_image()
        self.assertIsNotNone(image)
        self.assertEqual(image.width, 300)
        self.assertEqual(image.height, 100)
        print(f"✓ [PASS] Image generated: {image.width}x{image.height}")
    
    def test_generate_image_stores_code(self):
        """Test that generated image stores the code"""
        code = self.captcha.generate_code()
        self.captcha.generate_image(code)
        self.assertEqual(self.captcha.current_code, code)
        print(f"✓ [PASS] Code stored: {code}")
    
    def test_generate_image_file(self):
        """Test CAPTCHA image file generation"""
        output_path = os.path.join(self.temp_dir, 'test_captcha.png')
        path = self.captcha.generate_image_file(output_path=output_path)
        
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 0)
        print(f"✓ [PASS] Image file created: {path}")
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    
    def test_validate_correct_code(self):
        """Test validation with correct code"""
        code = "ABC123"
        self.captcha.current_code = code
        
        result = self.captcha.validate("ABC123")
        self.assertTrue(result)
        print(f"✓ [PASS] Correct code validated: {code}")
    
    def test_validate_case_insensitive(self):
        """Test validation is case-insensitive"""
        code = "ABC123"
        self.captcha.current_code = code
        
        # Test lowercase
        result = self.captcha.validate("abc123")
        self.assertTrue(result)
        
        # Test mixed case
        result = self.captcha.validate("AbC123")
        self.assertTrue(result)
        print(f"✓ [PASS] Case-insensitive validation works")
    
    def test_validate_incorrect_code(self):
        """Test validation with incorrect code"""
        self.captcha.current_code = "ABC123"
        
        result = self.captcha.validate("XYZ789")
        self.assertFalse(result)
        print("✓ [PASS] Incorrect code rejected")
    
    def test_validate_with_whitespace(self):
        """Test validation trims whitespace"""
        self.captcha.current_code = "ABC123"
        
        result = self.captcha.validate("  ABC123  ")
        self.assertTrue(result)
        print("✓ [PASS] Whitespace trimmed correctly")
    
    def test_validate_no_code_set(self):
        """Test validation fails when no code is set"""
        self.captcha.current_code = None
        
        result = self.captcha.validate("ABC123")
        self.assertFalse(result)
        print("✓ [PASS] Validation fails without code set")
    
    def test_get_code(self):
        """Test retrieving current code"""
        code = "XYZ789"
        self.captcha.current_code = code
        
        result = self.captcha.get_current_code()
        self.assertEqual(result, code)
        print(f"✓ [PASS] Code retrieved: {result}")
    
    def test_reset(self):
        """Test CAPTCHA reset"""
        self.captcha.current_code = "ABC123"
        self.captcha.current_image_path = "/some/path"
        
        self.captcha.reset()
        self.assertIsNone(self.captcha.current_code)
        self.assertIsNone(self.captcha.current_image_path)
        print("✓ [PASS] CAPTCHA reset successfully")
    
    def test_get_code_bytes(self):
        """Test getting image as bytes"""
        img_bytes = self.captcha.get_code_bytes()
        
        self.assertIsNotNone(img_bytes)
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)
        print(f"✓ [PASS] Image bytes generated: {len(img_bytes)} bytes")
    
    def test_sequential_captchas(self):
        """Test generating multiple sequential CAPTCHAs"""
        codes = []
        for i in range(5):
            code = self.captcha.generate_code()
            codes.append(code)
        
        # All codes should be unique (very high probability)
        unique_codes = set(codes)
        self.assertGreater(len(unique_codes), 3)
        print(f"✓ [PASS] Generated {len(codes)} sequential codes: {codes}")


class TestCaptchaValidationFlow(unittest.TestCase):
    """Test CAPTCHA validation workflow"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.captcha = CaptchaGenerator()
    
    def test_full_validation_flow(self):
        """Test complete validation flow"""
        # Generate CAPTCHA
        code = self.captcha.generate_code()
        self.captcha.generate_image(code)
        
        # User enters correct code
        result = self.captcha.validate(code)
        self.assertTrue(result)
        
        # Generate new CAPTCHA
        new_code = self.captcha.generate_code()
        self.captcha.generate_image(new_code)
        self.assertNotEqual(new_code, code)
        
        # Old code should not validate
        result = self.captcha.validate(code)
        self.assertFalse(result)
        
        print(f"✓ [PASS] Full flow: {code} → {new_code}")
    
    def test_failed_attempts_flow(self):
        """Test flow with failed CAPTCHA attempts"""
        code1 = self.captcha.generate_code()
        self.captcha.generate_image(code1)
        
        # First attempt fails
        result = self.captcha.validate("INVALID")
        self.assertFalse(result)
        
        # Generate new CAPTCHA
        code2 = self.captcha.generate_code()
        self.captcha.generate_image(code2)
        
        # Second attempt succeeds
        result = self.captcha.validate(code2)
        self.assertTrue(result)
        
        print(f"✓ [PASS] Failed attempt flow: INVALID → {code2}")


if __name__ == '__main__':
    print("=" * 70)
    print("CAPTCHA GENERATOR TEST SUITE")
    print("=" * 70)
    
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"OVERALL: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun} tests passed")
    print("=" * 70)
