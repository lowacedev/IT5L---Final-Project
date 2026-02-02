

class UserModel:

    def __init__(self, db):
        self.db = db
        from app.services.UserService import UserService
        self._service = UserService(db)

    def authenticate(self, username, password):
    
        return self._service.authenticate(username, password)