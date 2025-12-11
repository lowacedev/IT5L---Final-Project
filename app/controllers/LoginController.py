from PyQt6.QtWidgets import QMessageBox

class LoginController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        view.login_btn.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.view.username.text()
        password = self.view.password.text()

        user = self.model.authenticate(username, password)

        if user:
            self.view.accept()
            self.view.logged_in_user = user
        else:
            QMessageBox.warning(self.view, "Error", "Invalid username or password")
