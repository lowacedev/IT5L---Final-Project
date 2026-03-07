# Security Architecture Diagram & Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (PyQt6)                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Login View     │ Dashboard    │ Sales View  │ Reports View │  │
│  │ (Secure Login) │ (Role-based) │ (Validated) │ (Authorized) │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│            APPLICATION LOGIC LAYER (Controllers)                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ • Input Validation (InputValidator)                        │  │
│  │ • Role Checking (RBAC Manager)                            │  │
│  │ • Session Management (SessionManager)                     │  │
│  │ • Business Logic Execution                                │  │
│  │ • Activity Logging (SecurityAuditLogger)                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│         SECURITY SERVICES LAYER (Security Module)                 │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ ┌──────────────────────────────────────────────────────┐ │    │
│  │ │ AUTHENTICATION                                       │ │    │
│  │ │ • SecureUserService (registration, auth, pwd change)│ │    │
│  │ │ • PasswordManager (hashing, validation)             │ │    │
│  │ │ • LoginAttemptTracker (lockout mechanism)           │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  │                                                          │    │
│  │ ┌──────────────────────────────────────────────────────┐ │    │
│  │ │ AUTHORIZATION                                       │ │    │
│  │ │ • RBACManager (permissions, roles)                  │ │    │
│  │ │ • SessionManager (session tracking)                 │ │    │
│  │ │ • Permission Enforcement                            │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  │                                                          │    │
│  │ ┌──────────────────────────────────────────────────────┐ │    │
│  │ │ DATA PROTECTION                                      │ │    │
│  │ │ • DataEncryption (AES encryption/decryption)        │ │    │
│  │ │ • InputValidator (SQL injection prevention)         │ │    │
│  │ │ • Parameterized Queries                             │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  │                                                          │    │
│  │ ┌──────────────────────────────────────────────────────┐ │    │
│  │ │ LOGGING & MONITORING                                 │ │    │
│  │ │ • SecurityLogger (application logs)                  │ │    │
│  │ │ • SecurityAuditLogger (security events)              │ │    │
│  │ │ • Log Rotation & Management                          │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  │                                                          │    │
│  │ ┌──────────────────────────────────────────────────────┐ │    │
│  │ │ CONFIGURATION                                        │ │    │
│  │ │ • SecurityConfig (from .env)                         │ │    │
│  │ │ • Security Policies                                  │ │    │
│  │ │ • Validation Rules                                   │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│               DATABASE ACCESS LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ • Database Connection (secure config from .env)            │  │
│  │ • Parameterized Query Execution (SQL Injection Prevention) │  │
│  │ • Transaction Management                                   │  │
│  │ • Error Handling (safe messages)                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    MYSQL DATABASE                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Core Tables:            │ Security Tables:                 │  │
│  │ • users                 │ • security_audit_logs            │  │
│  │ • inventory_items       │ • user_sessions                  │  │
│  │ • sales                 │ • login_attempts                 │  │
│  │ • sale_items            │ • user_activity_logs             │  │
│  │ • suppliers             │ • access_control_logs            │  │
│  │ • stock_movements       │ • backup_logs                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Encryption At Rest: Sensitive fields encrypted (AES)             │
│  Audit Trail: All changes logged with timestamps                  │
│  Access Control: Database user permissions enforced               │
└──────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

```
User Enters Credentials
         │
         ▼
┌──────────────────────────────────────┐
│ Input Validation                     │
│ • Check username format              │
│ • Validate password not empty        │
│ • Prevent SQL injection              │
└────────────┬─────────────────────────┘
             │ (Valid inputs)
             ▼
┌──────────────────────────────────────┐
│ Check Login Lockout                  │
│ • Get failed attempts count          │
│ • Check if account locked            │
│ • Verify lockout duration expired    │
└────────────┬─────────────────────────┘
             │ (Not locked)
             ▼
┌──────────────────────────────────────┐
│ Query User (Parameterized Query)     │
│ SELECT * FROM users WHERE username=? │
└────────────┬─────────────────────────┘
             │ (User found)
             ▼
┌──────────────────────────────────────┐
│ Verify Password                      │
│ • Use bcrypt.checkpw()               │
│ • Compare plain password with hash   │
└────────────┬─────────────────────────┘
             │ (Password correct)
             ▼
┌──────────────────────────────────────┐
│ Check Account Active                 │
│ • Verify is_active = 1               │
└────────────┬─────────────────────────┘
             │ (Account active)
             ▼
┌──────────────────────────────────────┐
│ Log Successful Login                 │
│ • Record in security_audit_logs      │
│ • Update last_login_attempt          │
│ • Clear failed_login_attempts        │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Start Session                        │
│ • SessionManager.start_session()     │
│ • Store user_id, username, role      │
│ • Set session timeout                │
└────────────┬─────────────────────────┘
             │
             ▼
        LOGIN SUCCESS ✓
```

---

## Authorization (RBAC) Flow

```
User Attempts Action
         │
         ▼
┌──────────────────────────────────────┐
│ Check Authentication                 │
│ • Is user logged in?                 │
│ • Is session valid?                  │
│ • Is session not expired?            │
└────────────┬─────────────────────────┘
             │ (Authenticated)
             ▼
┌──────────────────────────────────────┐
│ Get User Role                        │
│ • Retrieve from SessionManager       │
│ • Enum: Admin, Manager, Cashier      │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Check Permission                     │
│ • RBACManager.can_perform_action()   │
│ • Check (resource, action) pair      │
│ • Verify role has permission         │
└────────────┬─────────────────────────┘
             │
        ┌────┴─────────┐
        │              │
   Allowed        Denied
        │              │
        ▼              ▼
    ALLOW ACTION   LOG DENIAL
                   Return Error
                   (Access Denied)
```

---

## Data Flow with Encryption

```
User Enters Sensitive Data
(Phone Number, Email, etc.)
         │
         ▼
┌──────────────────────────────────────┐
│ Input Validation                     │
│ • Format check                       │
│ • Sanitization                       │
│ • Injection prevention               │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Encryption                           │
│ • DataEncryption.encrypt()           │
│ • AES-128 (Fernet)                   │
│ • Return encrypted string            │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Database Storage                     │
│ • Store encrypted value              │
│ • Parameterized query                │
│ • Prevent SQL injection              │
└────────────┬─────────────────────────┘
             │
             ▼
    [Encrypted in Database]
             │
             ▼ (Read request)
┌──────────────────────────────────────┐
│ Authorization Check                  │
│ • Verify user has read access        │
│ • Log data access                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Decryption                           │
│ • DataEncryption.decrypt()           │
│ • Return plain text                  │
└────────────┬─────────────────────────┘
             │
             ▼
    Display to Authorized User
```

---

## Logging & Audit Trail

```
System Events
     │
     ├─────────────────┬─────────────────┐
     │                 │                 │
     ▼                 ▼                 ▼
Login Events      User Actions      System Events
     │                 │                 │
     ├─────────────┬─────────────┬─────────────┐
     │             │             │             │
  Success       Create User   Database       Errors
  Failed         Edit          Operations
  Locked        Delete         Config
                               Changes
                 │
                 ▼
     ┌──────────────────────────────┐
     │ SecurityAuditLogger          │
     │ • Log with timestamp         │
     │ • Include user info          │
     │ • Include resource/action    │
     │ • Include result (success)   │
     └────────────┬─────────────────┘
                  │
                  ▼
     ┌──────────────────────────────┐
     │ Logging System               │
     │ • File handler (10MB rotate) │
     │ • Console output             │
     │ • Structured format          │
     └────────────┬─────────────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
       ▼                     ▼
   logs/app.log      Database Tables
                     audit_logs
                     activity_logs
                     access_logs
```

---

## Security Validation Pipeline

```
Input from User
      │
      ▼
┌──────────────────────────────────────┐
│ Stage 1: Format Validation           │
│ • Length check                       │
│ • Character set check                │
│ • Type validation                    │
└────────────┬─────────────────────────┘
             │ (Invalid?) → Error to User
             │
             ▼ (Valid)
┌──────────────────────────────────────┐
│ Stage 2: Business Logic Validation   │
│ • Range checks (price, quantity)     │
│ • Uniqueness checks (username)       │
│ • Dependency checks                  │
└────────────┬─────────────────────────┘
             │ (Invalid?) → Error to User
             │
             ▼ (Valid)
┌──────────────────────────────────────┐
│ Stage 3: Security Validation         │
│ • SQL injection detection            │
│ • XSS prevention check               │
│ • Authorization check                │
└────────────┬─────────────────────────┘
             │ (Invalid?) → Error to User
             │           → Log attempt
             │
             ▼ (Valid)
┌──────────────────────────────────────┐
│ Stage 4: Sanitization                │
│ • Remove whitespace                  │
│ • Encode special characters          │
│ • Prepare for storage                │
└────────────┬─────────────────────────┘
             │
             ▼ (Safe to process)
         PROCEED WITH ACTION
         (Database operation, etc.)
```

---

## Password Security Flow

```
User Sets New Password
         │
         ▼
┌──────────────────────────────────────┐
│ Strength Validation                  │
│ • Min 8 characters                   │
│ • Requires uppercase                 │
│ • Requires lowercase                 │
│ • Requires numbers                   │
│ • Requires special characters        │
└────────────┬─────────────────────────┘
             │ (Weak?) → Error
             │
             ▼ (Strong)
┌──────────────────────────────────────┐
│ Hashing with Bcrypt                  │
│ • Generate salt (12 rounds)          │
│ • Hash password + salt               │
│ • Return hash ($2b$12$...)           │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Store in Database                    │
│ • Parameterized query                │
│ • Never store plain password         │
│ • Update password_changed_at         │
└────────────┬─────────────────────────┘
             │
             ▼
    PASSWORD SAVED ✓
```

---

## Role-Based Feature Access

```
        Admin              Manager            Cashier
         │                  │                   │
         ├─ Users Menu      ├─ Inventory      ├─ Sales
         ├─ Settings        ├─ Reports        └─ View Items
         ├─ Inventory       └─ (Limited)
         ├─ Reports
         ├─ Logs
         └─ Backup

┌────────────────────────────────────────────────────────┐
│          Permission Check on Feature Access           │
│                                                       │
│  1. Get current user role from SessionManager        │
│  2. Check RBACManager.can_access_feature(role, feat) │
│  3. If allowed: Show feature                         │
│  4. If denied: Hide feature + Log attempt            │
└────────────────────────────────────────────────────────┘
```

---

## Error Handling & Logging

```
Error Occurs in Application
         │
         ▼
┌──────────────────────────────────────┐
│ Exception Handling                   │
│ • Catch specific exception           │
│ • Extract error details              │
│ • Determine severity                 │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Log Internally                       │
│ • Full error message (logs/)         │
│ • Stack trace (debug mode)           │
│ • User context                       │
│ • Timestamp                          │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Show to User                         │
│ • Generic error message (no details) │
│ • Actionable information             │
│ • No stack traces                    │
│ • No SQL errors                      │
└────────────┬─────────────────────────┘
             │
             ▼
    USER SEES: "Operation failed. Please try again."
    LOG CONTAINS: Detailed technical information
```

---

## Security Components Interaction

```
                    ┌─────────────────────┐
                    │  SecurityConfig     │
                    │  (loads from .env)  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
   │ Password    │    │ Encryption   │    │ Input Validator  │
   │ Manager     │    │ (AES)        │    │ (SQL Prevention) │
   └──────┬──────┘    └──────┬───────┘    └────────┬─────────┘
          │                  │                     │
          └──────────────────┼─────────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ SecureUserService   │
                    │ (Authentication)    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌──────────┐   ┌──────────┐   ┌──────────────┐
         │ RBAC     │   │ Session  │   │ Logger       │
         │ Manager  │   │ Manager  │   │ (Audit)      │
         └──────────┘   └──────────┘   └──────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                        ┌─────────────────────┐
                        │  Database Connection│
                        │  (Secure Config)    │
                        └──────────┬──────────┘
                                   │
                                   ▼
                            MySQL Database
```

---

## Deployment Security Checklist

```
┌─────────────────────────────────────────┐
│ PRE-DEPLOYMENT SECURITY CHECKLIST       │
├─────────────────────────────────────────┤
│                                         │
│ Configuration:                          │
│ ☐ .env created with strong password    │
│ ☐ Encryption key (32+ chars)           │
│ ☐ DEBUG mode OFF                       │
│ ☐ Log files configured                 │
│                                         │
│ Database:                               │
│ ☐ Security migration applied           │
│ ☐ Admin user created                   │
│ ☐ Backup system configured             │
│ ☐ Test connection successful           │
│                                         │
│ Security:                               │
│ ☐ Password policy tested               │
│ ☐ Login lockout tested                 │
│ ☐ RBAC features verified               │
│ ☐ Encryption working                   │
│                                         │
│ Testing:                                │
│ ☐ Unit tests pass                      │
│ ☐ Bandit scan completed                │
│ ☐ Safety check passed                  │
│ ☐ All features tested                  │
│                                         │
│ Monitoring:                             │
│ ☐ Logs configured                      │
│ ☐ Log rotation set up                  │
│ ☐ Audit trail verified                 │
│ ☐ Error handling tested                │
│                                         │
└─────────────────────────────────────────┘
```

---

## Security Improvements Summary

```
BEFORE                          AFTER
─────────────────────────────────────────────────────
Plaintext passwords      →      Bcrypt hashing
No validation            →      Input validation
SQL vulnerable           →      Parameterized queries
No auth tracking         →      Login attempt tracking
No roles                 →      RBAC with 3 roles
No encryption            →      AES encryption
Hardcoded credentials    →      Environment variables
No logging               →      Comprehensive logging
No audit trail           →      Complete audit logs
No error safety          →      Safe error messages
No access control        →      Role-based UI control
─────────────────────────────────────────────────────
```

This comprehensive architecture ensures security at every layer of the application!
