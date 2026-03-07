# 🔧 Database Migration - Windows Setup Guide

## Problem
The `mysql` command is not recognized in PowerShell. This is because MySQL is not in your system PATH.

## Solutions

### ✅ Solution 1: Find MySQL Installation (Recommended)

First, locate your MySQL installation. It's typically in one of these locations:

```powershell
# Check common locations
Test-Path "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
Test-Path "C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"
Test-Path "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe"
```

Once you find the correct path, run:

```powershell
# For XAMPP (your setup)
$mysqlPath = "C:\xampp\mysql\bin\mysql.exe"
Get-Content sql/security_migration.sql | & $mysqlPath -u root -p computerparts_pos
```

Or more simply:

```powershell
# Direct XAMPP command
& "C:\xampp\mysql\bin\mysql.exe" -u root -p computerparts_pos < sql/security_migration.sql
```

### ✅ Solution 2: Add MySQL to PATH (Permanent)

1. Find your MySQL bin directory (from Solution 1)
2. Open **Environment Variables**:
   - Press `Win + X` → Choose **System**
   - Click **Advanced system settings**
   - Click **Environment Variables**
3. Click **New** under "System variables"
4. Variable name: `Path`
5. Variable value: `C:\Program Files\MySQL\MySQL Server 8.0\bin` (use your actual path)
6. Click **OK** and restart PowerShell

Then you can use:
```powershell
Get-Content sql/security_migration.sql | mysql -u root -p computerparts_pos
```

### ✅ Solution 3: Use MySQL Workbench

1. Open MySQL Workbench
2. File → Open SQL Script
3. Navigate to `sql/security_migration.sql`
4. Click **Execute** button

### ✅ Solution 4: Use Command Prompt (cmd.exe)

```cmd
mysql -u root -p computerparts_pos < sql/security_migration.sql
```

### ✅ Solution 5: Use Python Script

Create a file `run_migration.py`:

```python
import subprocess
import sys

try:
    # Read the SQL file
    with open('sql/security_migration.sql', 'r') as f:
        sql_commands = f.read()
    
    # Run MySQL with the SQL commands
    process = subprocess.Popen(
        ['mysql', '-u', 'root', '-p', 'computerparts_pos'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=sql_commands)
    
    if stderr:
        print(f"Error: {stderr}")
    else:
        print("Database migration completed successfully!")
        print(stdout)
    
except Exception as e:
    print(f"Error running migration: {e}")
    sys.exit(1)
```

Then run:
```bash
python run_migration.py
```

---

## 🔍 Verify MySQL Installation

Run this to find MySQL:

```powershell
# Search for mysql.exe in Program Files
Get-ChildItem -Path "C:\Program Files*" -Include "mysql.exe" -Recurse -ErrorAction SilentlyContinue
```

---

## ✅ After Migration

Once you've successfully run the migration, verify it worked:

```bash
python -m app.security.initializer
```

This will:
1. Setup logging
2. Validate configuration
3. Initialize encryption
4. Create required directories
5. Test database connection

---

## 📚 Next Steps

1. ✅ Find your MySQL path (Solution 1)
2. ✅ Run the migration using your preferred method
3. ✅ Run `python -m app.security.initializer`
4. ✅ Create admin user (see SECURITY_SETUP.md)
5. ✅ Continue with security setup

---

## 🆘 Still Having Issues?

If the migration still doesn't work, try this direct approach:

```powershell
# Start MySQL CLI directly
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p computerparts_pos
```

Then paste the contents of `sql/security_migration.sql` directly into the MySQL prompt.

---

**Note**: Replace `C:\Program Files\MySQL\MySQL Server 8.0\bin` with your actual MySQL installation path.
