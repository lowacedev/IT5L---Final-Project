#!/usr/bin/env python
from app.core.db import get_db

db = get_db()
c = db.cursor(dictionary=True)

c.execute('SELECT COUNT(*) as cnt FROM user_activity_logs')
count = c.fetchone()['cnt']

print(f'Total user_activity_logs records: {count}')

# Show latest 5
c.execute('SELECT username, action, details FROM user_activity_logs ORDER BY timestamp DESC LIMIT 5')
for row in c.fetchall():
    print(f'  - {row["username"]}: {row["action"]} - {row["details"][:50]}...')

c.close()
