#!/usr/bin/env python
from app.core.db import get_db

db = get_db()
cursor = db.cursor(dictionary=True)

# Check current state
cursor.execute('SELECT username, failed_login_attempts, last_login_attempt, locked_until FROM users')
users = cursor.fetchall()

print("User Database State:")
print("=" * 80)
for user in users:
    print(f"User: {user['username']}")
    print(f"  Failed Attempts: {user['failed_login_attempts']}")
    print(f"  Last Attempt: {user['last_login_attempt']}")
    print(f"  Locked Until: {user['locked_until']}")
    print()

cursor.close()
