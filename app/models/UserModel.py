class UserModel:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor(dictionary=False)  # Return tuples

    def authenticate(self, username, password):
        """Authenticate user and return user dict."""
        try:
            query = "SELECT id, username, role FROM users WHERE username=%s AND password=%s"
            self.cursor.execute(query, (username, password))
            result = self.cursor.fetchone()
            
            if result:
                # Convert tuple to dictionary
                return {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2]
                }
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None