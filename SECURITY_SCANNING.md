# Security Code Scanning Guide

## Tools Overview

This guide explains how to use security scanning tools to identify vulnerabilities in the Python codebase.

---

## 1. Bandit - Python AST-based Security Issue Finder

### Installation
```bash
pip install bandit
```

### Running Bandit

#### Scan entire project
```bash
bandit -r app/
```

#### Scan specific file
```bash
bandit app/services/SecureUserService.py
```

#### Scan with output to file
```bash
bandit -r app/ -f json -o bandit_report.json
```

#### Scan with severity filtering
```bash
bandit -r app/ -ll  # Only high and medium severity
```

### Common Issues Bandit Detects
- Hardcoded passwords
- SQL injection vulnerabilities
- Insecure random generation
- Use of assert statements
- Logging of passwords
- Pickle usage (unsafe)
- Weak cryptography

### Example Bandit Output
```
Issue: [B303:blacklist_call_with_pickle] Pickle can be exploited.
    Severity: High   Confidence: High
    Location: file.py:45
    Text: data = pickle.loads(input_data)
```

### Interpreting Results

**Severity Levels**:
- HIGH: Critical vulnerability
- MEDIUM: Potential security issue
- LOW: Possible issue or best practice

**Confidence Levels**:
- HIGH: Likely a real issue
- MEDIUM: Could be an issue
- LOW: Might be a false positive

---

## 2. Safety - Python Dependency Security Checker

### Installation
```bash
pip install safety
```

### Running Safety

#### Check installed packages
```bash
safety check
```

#### Check requirements.txt
```bash
safety check -r requirements.txt
```

#### Output as JSON
```bash
safety check --json
```

#### Check against different database
```bash
safety check --db https://safetycli.com/api/
```

### Example Safety Output
```
┌─────────────────────────────────────────────────────┐
│ Insecure Version in: flask==1.0.0                   │
├─────────────────────────────────────────────────────┤
│ Package: Flask                                      │
│ Version: 1.0.0                                      │
│ Vulnerability ID: 25853                             │
│ Description: Flask before 1.0.1 allows...           │
│ Recommended: Flask>=1.0.1                           │
└─────────────────────────────────────────────────────┘
```

---

## 3. Pylint with Security Plugins

### Installation
```bash
pip install pylint
```

### Running Pylint

#### Basic analysis
```bash
pylint app/services/SecureUserService.py
```

#### Disable specific warnings
```bash
pylint --disable=C0111,W0212 app/
```

#### Generate detailed report
```bash
pylint --reports=y app/ > pylint_report.txt
```

### Security-Related Pylint Checks
- `W0603`: Global statement usage
- `W0212`: Protected member access
- `E0401`: Import errors
- `C0301`: Line too long (can hide code)

---

## 4. Flake8 - Code Quality & Style

### Installation
```bash
pip install flake8
```

### Running Flake8
```bash
flake8 app/
```

### With plugins
```bash
pip install flake8-bandit
flake8 --select=B app/  # Run with bandit checks
```

---

## 5. Automated Security Scanning Script

Create `scan_security.sh`:

```bash
#!/bin/bash

echo "========================================="
echo "Security Code Scanning Report"
echo "========================================="
echo ""

echo "[1/4] Running Bandit (Security Issues)..."
bandit -r app/ -f json -o bandit_report.json
echo "✓ Bandit report saved to: bandit_report.json"
echo ""

echo "[2/4] Running Safety (Dependency Vulnerabilities)..."
safety check --json > safety_report.json || true
echo "✓ Safety report saved to: safety_report.json"
echo ""

echo "[3/4] Running Pylint (Code Quality)..."
pylint app/ --output-format=json > pylint_report.json || true
echo "✓ Pylint report saved to: pylint_report.json"
echo ""

echo "[4/4] Running Flake8 (Style & Quality)..."
flake8 app/ --format=json > flake8_report.json || true
echo "✓ Flake8 report saved to: flake8_report.json"
echo ""

echo "========================================="
echo "Scanning Complete!"
echo "========================================="
echo ""
echo "Summary Reports:"
echo "- Bandit:      bandit_report.json"
echo "- Safety:      safety_report.json"
echo "- Pylint:      pylint_report.json"
echo "- Flake8:      flake8_report.json"
```

Run it:
```bash
chmod +x scan_security.sh
./scan_security.sh
```

---

## 6. Continuous Security Scanning

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running security checks before commit..."

# Run bandit
bandit -r app/ -q || {
    echo "Bandit found security issues!"
    exit 1
}

# Run safety
safety check -q || {
    echo "Safety found vulnerable dependencies!"
    exit 1
}

echo "✓ Security checks passed!"
exit 0
```

Enable it:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 7. Security Best Practices Checklist

Use this checklist to manually review code for security:

### Input Validation
- [ ] All user inputs validated before use
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized output)
- [ ] Path traversal prevention

### Authentication
- [ ] Passwords hashed with bcrypt
- [ ] No plaintext passwords stored/logged
- [ ] Login attempts rate-limited
- [ ] Account lockout mechanism implemented

### Authorization
- [ ] RBAC enforced at application level
- [ ] Permission checks before data access
- [ ] Admin features restricted properly
- [ ] Audit log for access changes

### Cryptography
- [ ] Strong encryption algorithms used
- [ ] Keys stored securely (not hardcoded)
- [ ] Sensitive data encrypted at rest
- [ ] Secure random generation (not random module)

### Error Handling
- [ ] Generic error messages to users
- [ ] Detailed errors logged internally
- [ ] No stack traces exposed
- [ ] Secure error logging

### Data Protection
- [ ] Sensitive data not logged
- [ ] Database credentials from environment
- [ ] TLS/HTTPS for data in transit
- [ ] Secure session management

### Dependencies
- [ ] Regular updates checked
- [ ] Security advisories reviewed
- [ ] No EOL packages used
- [ ] Minimal dependencies

---

## 8. Fixing Common Security Issues

### Issue: Hardcoded Credentials
```python
# WRONG
password = "admin123"
db = connect("localhost", "root", "password")

# CORRECT
from app.security.config import SecurityConfig
db = connect(SecurityConfig.DB_HOST, SecurityConfig.DB_USER, SecurityConfig.DB_PASSWORD)
```

### Issue: SQL Injection
```python
# WRONG
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# CORRECT
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### Issue: Plaintext Password Logging
```python
# WRONG
logger.info(f"User {username} logged in with password {password}")

# CORRECT
logger.info(f"User {username} logged in successfully")
```

### Issue: Weak Random Generation
```python
# WRONG
import random
token = random.randint(0, 999999)

# CORRECT
import secrets
token = secrets.token_urlsafe(32)
```

---

## 9. Generate Security Report

Create comprehensive security report:

```python
import json
from datetime import datetime
import subprocess

def generate_security_report():
    """Generate comprehensive security report"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'scans': {}
    }
    
    # Run Bandit
    result = subprocess.run(['bandit', '-r', 'app/', '-f', 'json'], capture_output=True)
    report['scans']['bandit'] = json.loads(result.stdout)
    
    # Run Safety
    result = subprocess.run(['safety', 'check', '--json'], capture_output=True)
    report['scans']['safety'] = json.loads(result.stdout)
    
    # Save report
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("Security report generated: security_report.json")

if __name__ == '__main__':
    generate_security_report()
```

---

## 10. CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/security.yml`:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install bandit safety pylint
    
    - name: Bandit Scan
      run: bandit -r app/ -v
    
    - name: Safety Check
      run: safety check
    
    - name: Pylint
      run: pylint app/ --exit-zero
```

---

## Recommended Scanning Schedule

- **Before Commit**: Pre-commit hooks (Bandit + Safety)
- **On Push**: CI/CD pipeline (full scan)
- **Weekly**: Comprehensive audit
- **Monthly**: Dependency review
- **Quarterly**: Third-party security audit

---

## Resources

- Bandit: https://bandit.readthedocs.io/
- Safety: https://safety.readthedocs.io/
- Pylint: https://www.pylint.org/
- Flake8: https://flake8.pycqa.org/
- OWASP: https://owasp.org/
