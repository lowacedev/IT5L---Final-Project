import os
import sys


if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
from app.views.MainWindow import MainWindow
from app.views.LoginView import LoginView
from app.models.UserModel import UserModel
from app.core.db import get_db

class AuthController:
    """Simple authentication controller."""
    def __init__(self, db):
        self.user_model = UserModel(db)
    
    def login(self, username, password):
        """Authenticate user."""
        return self.user_model.authenticate(username, password)

def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')  
    
    try:
        db = get_db()
        
     
        auth_controller = AuthController(db)
        login_dialog = LoginView(auth_controller)
        
        if login_dialog.exec() == LoginView.DialogCode.Accepted:
            user = login_dialog.user
            
  
            window = MainWindow(user)
            window.show()
            
            sys.exit(app.exec())
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}")
   
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main() 