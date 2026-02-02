from app.exceptions import ValidationError, NotFoundError, DatabaseError


class LoginController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

        view.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        try:
            username, password = self.view.collect_form_data()
            
            if not username or not password:
                self.view.show_warning("Please enter username and password.")
                return
            
            user = self.service.authenticate(username, password)

            if user:
                self.view.accept()
                self.view.logged_in_user = user
            else:
                self.view.show_error("Invalid username or password.")
        except (ValidationError, NotFoundError, DatabaseError) as e:
            self.view.show_error(f"Login failed: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")
