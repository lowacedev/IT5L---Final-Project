class UserService:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor(dictionary=False)

    def authenticate(self, username, password):
        try:
            query = "SELECT id, username, full_name, role FROM users WHERE username=%s AND password=%s"
            self.cursor.execute(query, (username, password))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'full_name': result[2],
                    'role': result[3]
                }
            return None
            
        except Exception as e:
            print(f"[USER SERVICE ERROR] authenticate: {e}")
            return None
