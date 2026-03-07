"""
Input Validation and Sanitization Module
Validates and sanitizes user inputs to prevent injection attacks and invalid data.
"""

import re
from typing import Union, Tuple

class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # SQL-like keywords that might indicate injection attempts
    DANGEROUS_PATTERNS = [
        r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute|script|javascript|onerror|onload)",
        r"(--|;|\/\*|\*\/|xp_|sp_)",  # SQL comments and stored procedures
    ]
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username (str): Username to validate
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 50:
            return False, "Username must not exceed 50 characters"
        
        # Allow alphanumeric and underscores only
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False, "Username can only contain letters, numbers, dots, underscores, and hyphens"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email (str): Email to validate
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not email:
            return False, "Email cannot be empty"
        
        if len(email) > 100:
            return False, "Email must not exceed 100 characters"
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, "Email is valid"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not phone:
            return False, "Phone cannot be empty"
        
        # Remove spaces, dashes, and parentheses
        cleaned = re.sub(r'[\s\-().]', '', phone)
        
        # Check if only digits
        if not cleaned.isdigit():
            return False, "Phone must contain only digits and optional formatting characters"
        
        # Check length (10-15 digits for international)
        if len(cleaned) < 10 or len(cleaned) > 15:
            return False, "Phone must be 10-15 digits"
        
        return True, "Phone is valid"
    
    @staticmethod
    def validate_philippine_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate Philippine phone number format.
        Accepts formats:
        - 09XX XXXX XXX (11 digits with 0 prefix)
        - +63 9XX XXXX XXX (12 digits with +63 prefix)
        
        Args:
            phone (str): Philippine phone number to validate
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not phone:
            return False, "Phone cannot be empty"
        
        # Remove spaces, dashes, and parentheses
        cleaned = re.sub(r'[\s\-().]', '', phone)
        
        # Check if only digits and + sign
        if not re.match(r'^(\+\d+|\d+)$', cleaned):
            return False, "Phone must contain only digits"
        
        # Format 1: 09XX XXXX XXX (11 digits starting with 0)
        if cleaned.startswith('0'):
            if len(cleaned) == 11:
                return True, "Phone is valid"
            else:
                return False, f"Philippine number starting with 0 must be 11 digits, got {len(cleaned)}"
        
        # Format 2: +63 9XX XXXX XXX (63 + 10 digits = 12 characters including +)
        elif cleaned.startswith('+63'):
            digits_part = cleaned[3:]  # Remove '+63'
            if len(digits_part) == 10 and digits_part.startswith('9'):
                return True, "Phone is valid"
            else:
                return False, "Philippine +63 format must have 10 digits starting with 9"
        
        # Format 3: Just 10 digits starting with 9 (assumed PH)
        elif len(cleaned) == 10 and cleaned.startswith('9'):
            return True, "Phone is valid"
        
        else:
            return False, "Phone must be Philippine format: 09XX XXXX XXX, +63 9XX XXXX XXX, or 9XX XXXX XXX"
    
    @staticmethod
    def validate_numeric(value: Union[str, int, float], min_val=None, max_val=None) -> Tuple[bool, str]:
        """
        Validate numeric input.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        try:
            num = float(value)
            
            if min_val is not None and num < min_val:
                return False, f"Value must be at least {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"Value must not exceed {max_val}"
            
            return True, "Value is valid"
        except (ValueError, TypeError):
            return False, "Value must be a valid number"
    
    @staticmethod
    def validate_product_name(name: str) -> Tuple[bool, str]:
        """
        Validate product name.
        Allows: letters, numbers, spaces, hyphens, slashes, parentheses, periods, commas
        Forbidden: !@#$%^*&+={}[]|\\:;\"'<>?~`
        
        Args:
            name (str): Product name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not name:
            return False, "Product name cannot be empty"
        
        if len(name) < 2:
            return False, "Product name must be at least 2 characters"
        
        if len(name) > 200:
            return False, "Product name must not exceed 200 characters"
        
        # Forbidden special characters
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"\'<>?~`]'
        if re.search(forbidden_chars, name):
            return False, "Product name contains forbidden characters: ! @ # $ % ^ * + = { } [ ] | \\ : ; \" ' < > ? ~"
        
        # Allow alphanumeric, spaces, and safe special chars (hyphens, slashes, parentheses, periods, commas)
        if not re.match(r'^[a-zA-Z0-9\s\-/().,&]+$', name):
            return False, "Product name contains invalid characters. Use only: letters, numbers, spaces, - / ( ) . , &"
        
        return True, "Product name is valid"
    
    @staticmethod
    def validate_price(price: Union[str, float], allow_zero=False) -> Tuple[bool, str]:
        """
        Validate price input.
        
        Args:
            price: Price to validate
            allow_zero: Allow zero price
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        try:
            price_val = float(price)
            
            if price_val < 0:
                return False, "Price cannot be negative"
            
            if price_val == 0 and not allow_zero:
                return False, "Price must be greater than 0"
            
            # Check decimal places (max 2)
            if len(str(price).split('.')[-1]) > 2:
                return False, "Price must have maximum 2 decimal places"
            
            return True, "Price is valid"
        except (ValueError, TypeError):
            return False, "Price must be a valid number"
    
    @staticmethod
    def validate_quantity(quantity: Union[str, int]) -> Tuple[bool, str]:
        """
        Validate quantity input.
        
        Args:
            quantity: Quantity to validate
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        try:
            qty = int(quantity)
            
            if qty <= 0:
                return False, "Quantity must be greater than 0"
            
            if qty > 999999:
                return False, "Quantity exceeds maximum limit"
            
            return True, "Quantity is valid"
        except (ValueError, TypeError):
            return False, "Quantity must be a valid number"
    
    @staticmethod
    def validate_category(category: str) -> Tuple[bool, str]:
        """
        Validate category input.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            category (str): Category name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not category:
            return False, "Category cannot be empty"
        
        if len(category) < 2:
            return False, "Category must be at least 2 characters"
        
        if len(category) > 100:
            return False, "Category must not exceed 100 characters"
        
        # Check for forbidden special characters
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"\'<>?~`]'
        if re.search(forbidden_chars, category):
            return False, "Category contains forbidden characters"
        
        # Allow alphanumeric, spaces, and safe special chars
        if not re.match(r'^[a-zA-Z0-9\s\-/().,&]+$', category):
            return False, "Category contains invalid characters"
        
        return True, "Category is valid"
    
    @staticmethod
    def validate_brand(brand: str) -> Tuple[bool, str]:
        """
        Validate brand input.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            brand (str): Brand name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not brand:
            return False, "Brand cannot be empty"
        
        if len(brand) < 1:
            return False, "Brand must be at least 1 character"
        
        if len(brand) > 100:
            return False, "Brand must not exceed 100 characters"
        
        # Check for forbidden special characters
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"\'<>?~`]'
        if re.search(forbidden_chars, brand):
            return False, "Brand contains forbidden characters"
        
        # Allow alphanumeric, spaces, and safe special chars
        if not re.match(r'^[a-zA-Z0-9\s\-/().,&]+$', brand):
            return False, "Brand contains invalid characters"
        
        return True, "Brand is valid"
    
    @staticmethod
    def validate_model_number(model: str) -> Tuple[bool, str]:
        """
        Validate model number input.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            model (str): Model number
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not model:
            return False, "Model number cannot be empty"
        
        if len(model) < 1:
            return False, "Model number must be at least 1 character"
        
        if len(model) > 100:
            return False, "Model number must not exceed 100 characters"
        
        # Check for forbidden special characters
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"\'<>?~`]'
        if re.search(forbidden_chars, model):
            return False, "Model number contains forbidden characters"
        
        # Allow alphanumeric, spaces, hyphens, and periods (common in model numbers)
        if not re.match(r'^[a-zA-Z0-9\s\-/.]+$', model):
            return False, "Model number contains invalid characters"
        
        return True, "Model number is valid"
    
    @staticmethod
    def validate_supplier_name(name: str) -> Tuple[bool, str]:
        """
        Validate supplier name.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            name (str): Supplier name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not name:
            return False, "Supplier name cannot be empty"
        
        if len(name) < 2:
            return False, "Supplier name must be at least 2 characters"
        
        if len(name) > 150:
            return False, "Supplier name must not exceed 150 characters"
        
        # Check for forbidden special characters
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"\'<>?~`]'
        if re.search(forbidden_chars, name):
            return False, "Supplier name contains forbidden characters"
        
        # Allow alphanumeric, spaces, and safe special chars
        if not re.match(r'^[a-zA-Z0-9\s\-/().,&]+$', name):
            return False, "Supplier name contains invalid characters"
        
        return True, "Supplier name is valid"
    
    @staticmethod
    def validate_contact_person(name: str) -> Tuple[bool, str]:
        """
        Validate contact person name.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            name (str): Contact person name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not name:
            return False, "Contact person name cannot be empty"
        
        if len(name) < 2:
            return False, "Contact person name must be at least 2 characters"
        
        if len(name) > 100:
            return False, "Contact person name must not exceed 100 characters"
        
        # Check for forbidden special characters (apostrophes allowed for names like O'Brien)
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"<>?~`]'
        if re.search(forbidden_chars, name):
            return False, "Contact person name contains forbidden characters"
        
        # Allow alphanumeric, spaces, and hyphens
        if not re.match(r'^[a-zA-Z\s\-\']+$', name):
            return False, "Contact person name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, "Contact person name is valid"
    
    @staticmethod
    def validate_full_name(name: str) -> Tuple[bool, str]:
        """
        Validate staff full name.
        Forbidden: !@#$%^*+={}[]|\\:;\"'<>?~`
        
        Args:
            name (str): Full name
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not name:
            return False, "Full name cannot be empty"
        
        if len(name) < 2:
            return False, "Full name must be at least 2 characters"
        
        if len(name) > 100:
            return False, "Full name must not exceed 100 characters"
        
        # Check for forbidden special characters (apostrophes allowed for names like O'Brien)
        forbidden_chars = r'[!@#$%^*+={}[\]|\\:;"<>?~`]'
        if re.search(forbidden_chars, name):
            return False, "Full name contains forbidden characters"
        
        # Allow alphanumeric, spaces, and hyphens/apostrophes (for names like "Mary-Jane" or "O'Brien")
        if not re.match(r'^[a-zA-Z\s\-\']+$', name):
            return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, "Full name is valid"
    
    @staticmethod
    def validate_role(role: str) -> Tuple[bool, str]:
        """
        Validate staff role.
        
        Args:
            role (str): Role name (admin, cashier, etc)
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not role:
            return False, "Role cannot be empty"
        
        valid_roles = ['admin', 'cashier', 'manager']
        if role.lower() not in valid_roles:
            return False, f"Role must be one of: {', '.join(valid_roles)}"
        
        return True, "Role is valid"
    
    @staticmethod
    def sanitize_string(value: str, allow_special=False) -> str:
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove null characters
        value = value.replace('\x00', '')
        
        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        if not allow_special:
            # Remove special characters except common ones
            value = re.sub(r'[^a-zA-Z0-9\s\-._]', '', value)
        
        return value
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Check if input might contain SQL injection attempt.
        
        Args:
            value (str): Value to check
            
        Returns:
            bool: True if potentially dangerous, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Potential SQL injection detected: {value[:50]}")
                return True
        
        return False
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """
        Validate search query.
        
        Args:
            query (str): Search query
            
        Returns:
            Tuple: (is_valid: bool, message: str)
        """
        if not query:
            return False, "Search query cannot be empty"
        
        if len(query) > 100:
            return False, "Search query too long"
        
        if InputValidator.check_sql_injection(query):
            return False, "Invalid characters in search query"
        
        return True, "Search query is valid"


# Example usage
if __name__ == "__main__":
    validator = InputValidator()
    
    # Test username
    is_valid, msg = validator.validate_username("john_doe")
    print(f"Username validation: {is_valid} - {msg}")
    
    # Test email
    is_valid, msg = validator.validate_email("john@example.com")
    print(f"Email validation: {is_valid} - {msg}")
    
    # Test price
    is_valid, msg = validator.validate_price("29.99")
    print(f"Price validation: {is_valid} - {msg}")
    
    # Test SQL injection
    dangerous = "'; DROP TABLE users; --"
    is_dangerous = validator.check_sql_injection(dangerous)
    print(f"SQL injection check: {is_dangerous}")
