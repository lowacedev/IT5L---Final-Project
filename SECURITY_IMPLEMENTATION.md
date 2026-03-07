# POS System Security Implementation Guide

## 1. ARCHITECTURE OVERVIEW

### Security Layers

```
┌─────────────────────────────────────────────────────┐
│           PyQt6 GUI Layer                           │
│  (Role-based UI restriction, Input validation)      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│      Application Logic Layer                        │
│  (RBAC enforcement, Session management)             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│      Security Services Layer                        │
│  (Authentication, Encryption, Logging)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│      Database Layer                                 │
│  (Parameterized queries, Encrypted data storage)    │
└─────────────────────────────────────────────────────┘
```

### Security Components

1. **Authentication (AuthenticationManager)**
   - Bcrypt password hashing
   - Login attempt tracking
   - Account lockout mechanism

2. **Authorization (RBAC Manager)**
   - Role-based access control
   - Permission management
   - Feature-level access control

3. **Data Security**
   - AES encryption for sensitive data
   - Secure database credential management
   - Parameterized SQL queries

4. **Input Validation**
   - Username, email, phone validation
   - Numeric and price validation
   - SQL injection prevention

5. **Logging & Audit**
   - Security event logging
   - User activity tracking
   - Access control logging

---

## 2. DATABASE SCHEMA CHANGES

### New Security Columns (users table)
```sql
- is_active (BOOLEAN): Account active status
- failed_login_attempts (INT): Failed login counter
- last_login_attempt (TIMESTAMP): Last login attempt time
- locked_until (TIMESTAMP): Account lockout time
- password_changed_at (TIMESTAMP): Last password change
- last_ip (VARCHAR): Last login IP address
- require_password_change (BOOLEAN): Force password change on next login
```

### New Security Tables

1. **security_audit_logs**
   - Tracks login, logout, data access, and system events
   - Searchable by event type, username, timestamp

2. **user_sessions**
   - Manages active user sessions
   - Stores session tokens, IP addresses, last activity

3. **login_attempts**
   - Tracks all login attempts (success/failure)
   - Used for lockout mechanism

4. **user_activity_logs**
   - Logs all user actions (create, edit, delete)
   - Searchable by module and action

5. **access_control_logs**
   - Logs permission checks and denials
   - Audit trail for RBAC enforcement

6. **backup_logs**
   - Tracks database backups
   - Restore history

---

## 3. SECURITY CONFIGURATION (.env)

```ini
# Database (use strong password in production!)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=computerparts_pos
DB_PORT=3306

# Encryption key (must be 32+ characters)
ENCRYPTION_KEY=your_32_character_base64_encoded_key_here

# Password policy
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHARS=true
REQUIRE_NUMBERS=true
REQUIRE_UPPERCASE=true

# Login security
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=900  # 15 minutes

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

**IMPORTANT**: Never commit .env to version control!

---

## 4. PYTHON CODE EXAMPLES

### 4.1 Authentication Example

```python
from app.services.SecureUserService import SecureUserService
from app.core.db import get_db

# Initialize service
db = get_db()
user_service = SecureUserService(db)

# Register a new user
result = user_service.register_user(
    username='john_doe',
    password='SecurePass123!',
    full_name='John Doe',
    role='cashier'
)

if result['success']:
    print(f"User registered: {result['message']}")
else:
    print(f"Error: {result['message']}")

# Authenticate user
user = user_service.authenticate('john_doe', 'SecurePass123!')
if user:
    print(f"Welcome {user['full_name']}! Role: {user['role']}")
else:
    print("Authentication failed")
```

### 4.2 Password Security

```python
from app.security.password_manager import PasswordManager

# Validate password strength
is_valid, message = PasswordManager.validate_password_strength("MyPassword123!")
if is_valid:
    # Hash password before storing
    hashed = PasswordManager.hash_password("MyPassword123!")
    # Store hashed in database
else:
    print(f"Invalid: {message}")

# Verify password during login
if PasswordManager.verify_password("MyPassword123!", hashed_from_db):
    print("Password correct!")
```

### 4.3 Input Validation

```python
from app.security.input_validator import InputValidator

# Validate username
is_valid, msg = InputValidator.validate_username("john_doe")

# Validate email
is_valid, msg = InputValidator.validate_email("john@example.com")

# Validate price
is_valid, msg = InputValidator.validate_price("29.99")

# Check for SQL injection
if InputValidator.check_sql_injection(user_input):
    print("Dangerous input detected!")
```

### 4.4 Data Encryption

```python
from app.security.encryption import get_encryption

enc = get_encryption()

# Encrypt sensitive data
phone = "0712345678"
encrypted_phone = enc.encrypt(phone)
# Store encrypted_phone in database

# Decrypt when displaying
decrypted_phone = enc.decrypt(encrypted_phone)
print(f"Phone: {decrypted_phone}")

# Encrypt dictionary fields
customer = {
    'name': 'John Doe',
    'phone': '0712345678',
    'email': 'john@example.com'
}

encrypted = enc.encrypt_dict(customer, ['phone', 'email'])
# Store encrypted
```

### 4.5 RBAC (Role-Based Access Control)

```python
from app.security.rbac import get_session_manager, UserRole, RBACManager

# Get session manager
session = get_session_manager()

# Start user session
session.start_session(
    user_id=1,
    username='john_doe',
    role='admin'
)

# Check permission
if session.can_perform_action('users', 'manage'):
    # Allow user management
    print("User can manage users")
else:
    # Show error
    print("Access denied!")

# Check feature access
if session.can_access_feature('user_management'):
    # Show user management UI
    pass

# Get all accessible features
features = session.get_accessible_features()
# features = ['inventory_management', 'sales_management', 'reports', ...]
```

### 4.6 Secure Database Queries

```python
from app.core.db import get_db

db = get_db()
cursor = db.cursor(dictionary=True)

# CORRECT: Parameterized query (prevents SQL injection)
query = "SELECT id, name FROM products WHERE category = %s AND price > %s"
cursor.execute(query, (category, min_price))
results = cursor.fetchall()

# WRONG: String concatenation (SQL injection vulnerability!)
query = f"SELECT id, name FROM products WHERE category = '{category}' AND price > {min_price}"
cursor.execute(query)  # Unsafe!
```

### 4.7 Logging

```python
from app.utils.logger import get_logger, SecurityAuditLogger

# Get logger
logger = get_logger(__name__)
logger.info("User logged in")
logger.error("Database error occurred")

# Audit logging
SecurityAuditLogger.log_login_attempt('john', success=True, ip_address='192.168.1.1')
SecurityAuditLogger.log_user_action('john', 'create_product', 'CPU i7-12700')
SecurityAuditLogger.log_unauthorized_access_attempt('john', 'users', 'delete')
```

---

## 5. PYQT6 GUI SECURITY INTEGRATION

### 5.1 Secure Login View

```python
from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QLabel, QMessageBox
from app.services.SecureUserService import SecureUserService
from app.security.rbac import get_session_manager
from app.core.db import get_db

class SecureLoginView(QDialog):
    def __init__(self):
        super().__init__()
        self.user_service = SecureUserService(get_db())
        self.setup_ui()
    
    def setup_ui(self):
        # Create UI components
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        
        # Add to layout...
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        # Authenticate
        user = self.user_service.authenticate(username, password)
        
        if user:
            # Start session
            session = get_session_manager()
            session.start_session(user['id'], user['username'], user['role'])
            
            QMessageBox.information(self, "Success", f"Welcome {user['full_name']}")
            self.accept()  # Close dialog
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials")
            self.password_input.clear()
```

### 5.2 Role-Based UI Restrictions

```python
from app.security.rbac import get_session_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = get_session_manager()
        self.setup_menu()
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Only show "Users" menu to admins
        if self.session.can_access_feature('user_management'):
            users_menu = menubar.addMenu("Users")
            users_menu.addAction("Manage Users", self.open_user_management)
        
        # Only show "Settings" menu to admins
        if self.session.can_access_feature('settings'):
            settings_menu = menubar.addMenu("Settings")
            # Add settings actions...
        
        # Show "Reports" to managers and admins
        if self.session.can_access_feature('reports'):
            reports_menu = menubar.addMenu("Reports")
            # Add report actions...
        
        # All users can access sales
        sales_menu = menubar.addMenu("Sales")
        sales_menu.addAction("New Sale", self.open_new_sale)
    
    def open_user_management(self):
        # Check permission before opening
        if not self.session.can_perform_action('users', 'manage'):
            QMessageBox.critical(self, "Access Denied", "You don't have permission to manage users")
            return
        
        # Open user management dialog
        dialog = UserManagementDialog(self.session)
        dialog.exec()
```

### 5.3 Input Validation in Forms

```python
from PyQt6.QtWidgets import QLineEdit, QMessageBox
from app.security.input_validator import InputValidator

class ProductForm(QDialog):
    def __init__(self):
        super().__init__()
        self.product_name = QLineEdit()
        self.price = QLineEdit()
        self.quantity = QLineEdit()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_product)
    
    def save_product(self):
        # Validate product name
        name = self.product_name.text()
        is_valid, msg = InputValidator.validate_product_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", msg)
            return
        
        # Validate price
        price = self.price.text()
        is_valid, msg = InputValidator.validate_price(price)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", msg)
            return
        
        # Validate quantity
        quantity = self.quantity.text()
        is_valid, msg = InputValidator.validate_quantity(quantity)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", msg)
            return
        
        # All valid, save to database
        self.save_to_database(name, float(price), int(quantity))
    
    def save_to_database(self, name, price, quantity):
        # Use parameterized query
        cursor = self.db.cursor()
        query = "INSERT INTO inventory_items (part_name, selling_price, quantity) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, price, quantity))
        self.db.commit()
        
        QMessageBox.information(self, "Success", "Product saved successfully")
```

### 5.4 Real-time Password Strength Indicator

```python
from PyQt6.QtWidgets import QLineEdit, QLabel, QProgressBar
from app.security.password_manager import PasswordManager

class PasswordStrengthWidget(QLineEdit):
    def __init__(self):
        super().__init__()
        self.strength_bar = QProgressBar()
        self.strength_label = QLabel()
        
        self.textChanged.connect(self.check_strength)
    
    def check_strength(self):
        password = self.text()
        
        # Check strength
        complexity = PasswordManager.validate_password_complexity(password)
        
        # Calculate strength score (0-4)
        score = sum([
            complexity['has_lowercase'],
            complexity['has_uppercase'],
            complexity['has_numbers'],
            complexity['has_special'],
        ])
        
        # Update visual feedback
        self.strength_bar.setValue(score * 25)  # 0-100%
        
        strength_text = ["Very Weak", "Weak", "Fair", "Good", "Strong"][score]
        self.strength_label.setText(f"Strength: {strength_text}")
```

---

## 6. LOGGING IMPLEMENTATION

### Log File Locations
```
logs/
├── app.log                 # General application log
└── (Rotated logs)
```

### Log Levels
- **INFO**: General information (logins, user actions)
- **WARNING**: Non-critical issues (failed login, unused features)
- **ERROR**: Recoverable errors (query failures)
- **CRITICAL**: Fatal errors (database connection failure)

### Log Format
```
[2024-01-15 14:30:45] INFO [app.services.UserService:45] - User logged in: john_doe
[2024-01-15 14:31:20] WARNING [app.security.auth:120] - Failed login attempt for: admin
[2024-01-15 14:32:10] ERROR [app.core.db:55] - Database query failed
```

### Audit Events Logged
- Login attempts (success/failure)
- Password changes
- User account creation/deletion
- Permission changes
- Data access
- System configuration changes
- Error events

---

## 7. TESTING

### 7.1 Test Authentication

```python
import unittest
from app.services.SecureUserService import SecureUserService
from app.core.db import get_db

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.db = get_db()
        self.user_service = SecureUserService(self.db)
    
    def test_register_valid_user(self):
        result = self.user_service.register_user(
            'testuser',
            'TestPass123!',
            'Test User',
            'cashier'
        )
        self.assertTrue(result['success'])
    
    def test_register_weak_password(self):
        result = self.user_service.register_user(
            'testuser',
            'weak',
            'Test User',
            'cashier'
        )
        self.assertFalse(result['success'])
        self.assertIn('characters', result['message'])
    
    def test_authenticate_valid_credentials(self):
        self.user_service.register_user(
            'testuser',
            'TestPass123!',
            'Test User'
        )
        
        user = self.user_service.authenticate('testuser', 'TestPass123!')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
    
    def test_authenticate_invalid_password(self):
        self.user_service.register_user(
            'testuser',
            'TestPass123!',
            'Test User'
        )
        
        user = self.user_service.authenticate('testuser', 'WrongPassword')
        self.assertIsNone(user)
    
    def test_login_lockout(self):
        self.user_service.register_user(
            'testuser',
            'TestPass123!',
            'Test User'
        )
        
        # Attempt 5 failed logins
        for i in range(5):
            self.user_service.authenticate('testuser', 'WrongPassword')
        
        # 6th attempt should fail (account locked)
        user = self.user_service.authenticate('testuser', 'TestPass123!')
        self.assertIsNone(user)
```

### 7.2 Test Input Validation

```python
import unittest
from app.security.input_validator import InputValidator

class TestInputValidation(unittest.TestCase):
    def test_valid_username(self):
        is_valid, msg = InputValidator.validate_username('john_doe')
        self.assertTrue(is_valid)
    
    def test_invalid_username_short(self):
        is_valid, msg = InputValidator.validate_username('ab')
        self.assertFalse(is_valid)
    
    def test_valid_email(self):
        is_valid, msg = InputValidator.validate_email('john@example.com')
        self.assertTrue(is_valid)
    
    def test_invalid_email(self):
        is_valid, msg = InputValidator.validate_email('invalid-email')
        self.assertFalse(is_valid)
    
    def test_valid_price(self):
        is_valid, msg = InputValidator.validate_price('29.99')
        self.assertTrue(is_valid)
    
    def test_negative_price(self):
        is_valid, msg = InputValidator.validate_price('-10')
        self.assertFalse(is_valid)
    
    def test_sql_injection_detection(self):
        dangerous = "'; DROP TABLE users; --"
        is_dangerous = InputValidator.check_sql_injection(dangerous)
        self.assertTrue(is_dangerous)
```

### 7.3 Test RBAC

```python
import unittest
from app.security.rbac import get_session_manager, UserRole

class TestRBAC(unittest.TestCase):
    def setUp(self):
        self.session = get_session_manager()
    
    def test_admin_permissions(self):
        self.session.start_session(1, 'admin', 'admin')
        
        self.assertTrue(self.session.can_perform_action('users', 'manage'))
        self.assertTrue(self.session.can_perform_action('logs', 'read'))
        self.assertTrue(self.session.can_access_feature('user_management'))
    
    def test_cashier_permissions(self):
        self.session.start_session(2, 'cashier', 'cashier')
        
        self.assertTrue(self.session.can_perform_action('sales', 'create'))
        self.assertFalse(self.session.can_perform_action('users', 'manage'))
        self.assertFalse(self.session.can_access_feature('user_management'))
    
    def test_feature_access_control(self):
        self.session.start_session(2, 'cashier', 'cashier')
        features = self.session.get_accessible_features()
        
        self.assertNotIn('user_management', features)
        self.assertNotIn('system_logs', features)
```

---

## 8. SECURITY POLICIES

### Password Policy
- **Minimum Length**: 8 characters
- **Complexity Requirements**:
  - At least one uppercase letter (A-Z)
  - At least one lowercase letter (a-z)
  - At least one number (0-9)
  - At least one special character (!@#$%^&*)
- **Expiration**: Optional (configure in .env)
- **Password History**: Don't allow reuse of last 5 passwords

### Login Attempt Policy
- **Max Failed Attempts**: 5 consecutive failures
- **Lockout Duration**: 15 minutes
- **Auto-unlock**: After lockout period expires

### Encryption Policy
- **Data to Encrypt**: Customer phone numbers, email addresses, API keys
- **Algorithm**: AES-128 (Fernet)
- **Key Management**: Stored in .env file, never hardcoded

### Logging Policy
- **Log Retention**: 90 days minimum
- **Events to Log**:
  - All login attempts (success/failure)
  - Password changes
  - User role changes
  - Permission denials
  - Data modifications
  - System errors
- **Log Format**: ISO 8601 timestamp + event details

### Access Control Policy
- **Role-Based**: Admin, Manager, Cashier
- **Principle of Least Privilege**: Users get minimum required permissions
- **Feature Restrictions**: Enforce at both backend and UI level

### Backup Policy
- **Frequency**: Daily at 2:00 AM (configurable)
- **Retention**: Keep 7 daily backups
- **Location**: `backups/` directory (encrypted if possible)
- **Testing**: Weekly restore tests

### Code Review & Security Auditing
- **Scanning Tools**:
  - Bandit: Check for common security issues
  - Safety: Check for vulnerable dependencies
  - Pylint: Code quality

### Incident Response
1. **Detect**: Monitor logs for suspicious activity
2. **Respond**: Lock accounts, disable features if needed
3. **Document**: Log all incident details
4. **Review**: Analyze root cause
5. **Update**: Implement preventive measures

---

## 9. DEPLOYMENT CHECKLIST

- [ ] Update .env with production database credentials
- [ ] Generate new encryption key (32+ characters)
- [ ] Run database migration: `mysql < sql/security_migration.sql`
- [ ] Create admin user with strong password
- [ ] Test all authentication flows
- [ ] Verify RBAC controls are working
- [ ] Enable debug mode OFF in .env
- [ ] Setup automated backups
- [ ] Configure log rotation
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Enable HTTPS for any API endpoints
- [ ] Setup monitoring/alerting for logs

---

## 10. SECURITY TOOLS

### Bandit (Security Checker)
```bash
pip install bandit
bandit -r app/  # Scan all Python files
```

### Safety (Dependency Checker)
```bash
pip install safety
safety check  # Check for vulnerable packages
```

### Running Tests
```bash
python -m pytest tests/  # Run all tests
```

---

## References

- OWASP Top 10: https://owasp.org/Top10/
- Python bcrypt: https://pypi.org/project/bcrypt/
- Cryptography library: https://cryptography.io/
- PyQt6 security: https://doc.qt.io/qt-6/security.html
