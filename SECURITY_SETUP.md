# Security Setup & Configuration Guide

## Quick Start

### 1. Install Security Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `bcrypt` - Password hashing
- `cryptography` - Data encryption
- `python-dotenv` - Environment variable management
- `bandit` - Security scanning
- `safety` - Dependency vulnerability checking

### 2. Create .env File

```bash
# Copy the example
cp .env.example .env

# Edit with your settings
# IMPORTANT: Set secure database password and encryption key
```

**Important environment variables:**

```ini
# Database credentials (use strong password!)
DB_PASSWORD=YourSecurePassword123!

# Generate encryption key (32+ characters)
ENCRYPTION_KEY=your_very_long_and_secure_encryption_key_32_chars_minimum
```

### 3. Generate Encryption Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output to `ENCRYPTION_KEY` in `.env`.

### 4. Update Database

**Windows PowerShell:**
```powershell
Get-Content sql/security_migration.sql | mysql -u root -p computerparts_pos
```

**Linux/Mac/Git Bash:**
```bash
mysql -u root -p computerparts_pos < sql/security_migration.sql
```

When prompted, enter your MySQL password.

### 5. Initialize Security

```bash
python -m app.security.initializer
```

### 6. Create Admin User

```python
from app.core.db import get_db
from app.services.SecureUserService import SecureUserService

db = get_db()
service = SecureUserService(db)

result = service.register_user(
    username='admin',
    password='AdminSecure123!',  # CHANGE THIS!
    full_name='System Administrator',
    role='admin'
)

print(result['message'])
db.close()
```

---

## Configuration Details

### .env File Settings

```ini
# ===== DATABASE =====
DB_HOST=localhost              # MySQL host
DB_USER=root                   # MySQL user
DB_PASSWORD=your_password      # MUST BE CHANGED
DB_NAME=computerparts_pos      # Database name
DB_PORT=3306                   # MySQL port

# ===== ENCRYPTION =====
ENCRYPTION_KEY=your_key_here   # 32+ character key

# ===== PASSWORD POLICY =====
MIN_PASSWORD_LENGTH=8          # Minimum password length
REQUIRE_SPECIAL_CHARS=true     # Need special characters
REQUIRE_NUMBERS=true           # Need numbers
REQUIRE_UPPERCASE=true         # Need uppercase

# ===== LOGIN SECURITY =====
MAX_LOGIN_ATTEMPTS=5           # Failed attempts before lockout
LOGIN_LOCKOUT_DURATION=900     # Lockout time in seconds (15 min)
SESSION_TIMEOUT=3600           # Session timeout in seconds (1 hour)

# ===== LOGGING =====
LOG_LEVEL=INFO                 # INFO, DEBUG, WARNING, ERROR
LOG_FILE=logs/app.log          # Log file location

# ===== BACKUP =====
BACKUP_ENABLED=true            # Enable automatic backups
BACKUP_DIR=backups/            # Backup directory

# ===== SECURITY =====
DEBUG=false                    # Set to false in production!
```

---

## Security Checklist

### Before First Run
- [ ] Create `.env` file with secure password
- [ ] Generate encryption key
- [ ] Run database migration
- [ ] Create admin user
- [ ] Test login with admin account

### Before Production
- [ ] Change default admin password
- [ ] Enable DEBUG=false in .env
- [ ] Use strong database password (20+ characters)
- [ ] Backup encryption key securely
- [ ] Enable automated backups
- [ ] Configure log rotation
- [ ] Test backup restoration
- [ ] Review security settings
- [ ] Run security scans (Bandit, Safety)

### Ongoing
- [ ] Monitor audit logs daily
- [ ] Review failed login attempts
- [ ] Update dependencies monthly
- [ ] Run security scans weekly
- [ ] Test disaster recovery quarterly

---

## Troubleshooting

### "ENCRYPTION_KEY not found"
**Problem**: `ENCRYPTION_KEY` not in .env file

**Solution**:
1. Open `.env` file
2. Generate key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Add: `ENCRYPTION_KEY=<generated_key>`
4. Save and restart

### "Database connection failed"
**Problem**: Cannot connect to MySQL

**Solution**:
1. Check MySQL is running
2. Verify credentials in .env
3. Ensure database exists: `CREATE DATABASE IF NOT EXISTS computerparts_pos;`
4. Check port (default 3306)

### "Invalid encryption key"
**Problem**: Key too short or invalid format

**Solution**:
1. Generate new key (32+ characters)
2. `ENCRYPTION_KEY` must be alphanumeric or URL-safe
3. Update .env and restart

### "Account locked"
**Problem**: Too many failed login attempts

**Solution**:
1. Wait 15 minutes (or configured duration)
2. Or, manually unlock in database:
   ```sql
   UPDATE users SET locked_until = NULL WHERE username = 'admin';
   ```

---

## Running Security Tests

### Unit Tests
```bash
python tests/test_security.py
```

### Security Scans

#### Bandit (Security Issues)
```bash
bandit -r app/
```

#### Safety (Vulnerable Dependencies)
```bash
safety check
```

#### Pylint (Code Quality)
```bash
pylint app/
```

### All Tests
```bash
python -m pytest tests/ -v
```

---

## Monitoring & Maintenance

### View Logs
```bash
tail -f logs/app.log  # Real-time
cat logs/app.log      # Full log
```

### Database Audit Events
```sql
-- View recent login attempts
SELECT * FROM security_audit_logs 
WHERE event_type = 'LOGIN' 
ORDER BY timestamp DESC 
LIMIT 20;

-- View failed logins
SELECT * FROM login_attempts 
WHERE success = 0 
ORDER BY attempt_time DESC;

-- View user actions
SELECT * FROM user_activity_logs 
ORDER BY timestamp DESC 
LIMIT 50;
```

### Database Backups

#### Manual Backup
```bash
mysqldump -u root -p computerparts_pos > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Restore from Backup
```bash
mysql -u root -p computerparts_pos < backup_20240115_120000.sql
```

---

## Password Management

### Change Your Password
```python
from app.core.db import get_db
from app.services.SecureUserService import SecureUserService

db = get_db()
service = SecureUserService(db)

result = service.change_password(
    username='admin',
    old_password='OldPassword123!',
    new_password='NewPassword456!'
)

print(result['message'])
```

### Reset User Password (Admin Only)
```python
from app.core.db import get_db
from app.security.password_manager import PasswordManager

db = get_db()
cursor = db.cursor()

# Hash new password
new_password = 'TempPassword123!'
hashed = PasswordManager.hash_password(new_password)

# Update user
query = "UPDATE users SET password = %s WHERE username = %s"
cursor.execute(query, (hashed, 'username_to_reset'))
db.commit()

print(f"Password reset to: {new_password}")
print("User should change password on next login")
```

---

## Updating Security Settings

### Change Password Policy
Edit `.env`:
```ini
MIN_PASSWORD_LENGTH=10
REQUIRE_SPECIAL_CHARS=true
REQUIRE_NUMBERS=true
REQUIRE_UPPERCASE=true
```

Restart application for changes to take effect.

### Change Login Attempt Policy
Edit `.env`:
```ini
MAX_LOGIN_ATTEMPTS=5        # Increase for more lenient policy
LOGIN_LOCKOUT_DURATION=900  # Decrease for shorter lockout
```

### Change Session Timeout
Edit `.env`:
```ini
SESSION_TIMEOUT=3600  # 1 hour
```

---

## Backup & Recovery

### Automated Backups
Set in `.env`:
```ini
BACKUP_ENABLED=true
BACKUP_DIR=backups/
```

Backups are created daily at 2:00 AM (configurable).

### Manual Backup
```bash
mysqldump -u root -p computerparts_pos > backups/manual_backup_$(date +%s).sql
```

### Restore Database
```bash
mysql -u root -p computerparts_pos < backups/backup_file.sql
```

### Verify Backup
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM inventory_items;
SELECT COUNT(*) FROM sales;
```

---

## Support & Resources

### Documentation
- `SECURITY_IMPLEMENTATION.md` - Detailed security guide
- `SECURITY_SCANNING.md` - Security scanning tools guide
- Requirements: `requirements.txt`

### Tools
- Bandit: Security scanning
- Safety: Dependency checking
- Pytest: Testing framework

### External Resources
- [OWASP Top 10](https://owasp.org/Top10/)
- [bcrypt Documentation](https://pypi.org/project/bcrypt/)
- [Python cryptography](https://cryptography.io/)
- [PyQt6 Security](https://doc.qt.io/qt-6/security.html)

---

## Contact & Issues

If you encounter security issues:
1. Check logs in `logs/app.log`
2. Review configuration in `.env`
3. Consult troubleshooting section above
4. Run security scans to identify issues
