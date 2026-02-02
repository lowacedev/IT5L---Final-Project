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
from app.services.UserService import UserService
from app.controllers.LoginController import LoginController
from app.core.db import get_db

def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')  
    
    try:
        db = get_db()
        
        user_service = UserService(db)
        login_view = LoginView()
        login_controller = LoginController(user_service, login_view)
        
        if login_view.exec() == LoginView.DialogCode.Accepted:
            user = login_view.logged_in_user
            
  
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
