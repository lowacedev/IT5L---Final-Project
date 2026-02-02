
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal


class BaseView(QWidget):
   
  
    refresh_requested = pyqtSignal()

    back_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.parent_view = None
    
    def show_error(self, message: str, title: str = "Error"):
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, message: str, title: str = "Warning"):
        QMessageBox.warning(self, title, message)
    
    def show_success(self, message: str, title: str = "Success"):
        QMessageBox.information(self, title, message)
    
    def show_info(self, message: str, title: str = "Information"):
        QMessageBox.information(self, title, message)
    
    def ask_confirmation(self, message: str, title: str = "Confirm") -> bool:
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def clear_form(self):
        pass
    
    def disable_form(self):
        pass
    
    def enable_form(self):
        pass
    
    def is_valid(self) -> bool:
        return True
