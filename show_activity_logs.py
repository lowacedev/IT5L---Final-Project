#!/usr/bin/env python
"""Show detailed user_activity_logs records"""

from app.core.db import get_db
from datetime import datetime

db = get_db()
c = db.cursor(dictionary=True)

c.execute('''
SELECT id, user_id, username, action, module, details, timestamp 
FROM user_activity_logs 
ORDER BY timestamp DESC 
LIMIT 20
''')

records = c.fetchall()

print("=" * 100)
print("USER ACTIVITY LOGS - LATEST RECORDS")
print("=" * 100)
print(f"\nTotal Records: {len(records)}\n")

for i, rec in enumerate(records, 1):
    print(f"{i}. [{rec['timestamp']}] {rec['username']} (user_id: {rec['user_id']})")
    print(f"   Action: {rec['action']}")
    print(f"   Details: {rec['details']}")
    print()

c.close()

# Summary
print("=" * 100)
print("SUMMARY")
print("=" * 100)
c = db.cursor(dictionary=True)
c.execute("SELECT COUNT(DISTINCT user_id) as unique_users, COUNT(*) as total_records FROM user_activity_logs")
stats = c.fetchone()
print(f"Unique users: {stats['unique_users']}")
print(f"Total records: {stats['total_records']}")

c.execute("""
SELECT username, COUNT(*) as count 
FROM user_activity_logs 
GROUP BY username 
ORDER BY count DESC
""")
print("\nRecords by user:")
for row in c.fetchall():
    print(f"  - {row['username']}: {row['count']} records")

c.close()
