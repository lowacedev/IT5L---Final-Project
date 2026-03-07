from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QMessageBox, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.views.Sidebar import Sidebar
from app.views.InventoryView import InventoryView
from app.views.POSView import POSView
from app.views.DashboardView import DashboardView
from app.views.ReportsView import ReportsView
from app.services.InventoryService import InventoryService
from app.services.SupplierService import SupplierService
from app.services.POSService import POSService
from app.services.ReportsService import ReportsService
from app.controllers.InventoryController import InventoryController
from app.controllers.POSController import POSController
from app.controllers.ReportsController import ReportsController
from app.core.db import get_db

class MainWindow(QMainWindow):
    def __init__(self, user=None, db_connection=None):
        super().__init__()
        
        self.user = user or {"username": "admin", "role": "admin"}
        self.db_connection = db_connection
        self.setWindowTitle("TechBayan")
        self.resize(1400, 800)
        
        # Load stylesheet
        try:
            with open("app/styles/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

       
        header_bar = QWidget()
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(16, 10, 16, 10)

    
        header_layout.addStretch()

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setObjectName("logout_button")
        self.btn_logout.clicked.connect(self.logout)
        header_layout.addWidget(self.btn_logout)

        main_layout.addWidget(header_bar)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

       
        self.apply_role_permissions()

   
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        main_layout.addWidget(container)

        self.setCentralWidget(main_widget)

 
        self.sidebar.btn_dashboard.clicked.connect(self.load_dashboard)
        self.sidebar.btn_pos.clicked.connect(self.load_pos)
        self.sidebar.btn_inventory.clicked.connect(self.load_inventory)
        self.sidebar.btn_reports.clicked.connect(self.load_reports)
        self.sidebar.btn_suppliers.clicked.connect(self.load_suppliers)
        self.sidebar.btn_staff.clicked.connect(self.load_staff)
        self.sidebar.btn_audit_logs.clicked.connect(self.load_audit_logs)

        
        try:
            if self._can_access('pos') and not self._can_access('dashboard'):
                print(f"[MainWindow.__init__] Loading POS for user: {self.user.get('username')} (role: {self.user.get('role')})")
                self.load_pos()
            elif self._can_access('dashboard'):
                print("[MainWindow.__init__] Loading Dashboard...")
                self.load_dashboard()
            elif self._can_access('inventory'):
                print("[MainWindow.__init__] Loading Inventory...")
                self.load_inventory()
            elif self._can_access('reports'):
                print("[MainWindow.__init__] Loading Reports...")
                self.load_reports()
        except Exception as e:
            print(f"[MainWindow.__init__ ERROR] Failed to load initial page: {e}")
            import traceback
            traceback.print_exc()
            # Show error message but don't crash
            error_label = QLabel(f"Failed to load page: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(error_label)

    def clear_stack(self):
        """Clear all widgets from stack."""
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def load_dashboard(self):
        self.clear_stack()
        self.sidebar.set_active("dashboard")
        
        try:
            db = get_db()
            from app.services.DashboardService import DashboardService
            from app.services.ReportsService import ReportsService
            from app.controllers.DashboardController import DashboardController
            
            dashboard_service = DashboardService(db)
            reports_service = ReportsService(db)
            view = DashboardView(db, self.user, reports_service)
            self.dashboard_controller = DashboardController(dashboard_service, view)
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.warning(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}")
            label = QLabel(f"Dashboard - Database Connection Error")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #6B7280; font-size: 16px; padding: 20px;")
            self.stack.addWidget(label)

    def load_pos(self):
        self.clear_stack()
        self.sidebar.set_active("pos")
        if not self._can_access('pos'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access the Point of Sale.")
            return
        
        try:
            db = get_db()
            view = POSView()
            service = POSService(db)
            self.pos_controller = POSController(service, view, self.user)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def load_inventory(self):
        self.clear_stack()
        self.sidebar.set_active("inventory")
        if not self._can_access('inventory'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access Inventory.")
            return
        
        try:
            db = get_db()
            supplier_service = SupplierService(db)
            view = InventoryView(supplier_service=supplier_service, user=self.user)
            service = InventoryService(db)
            self.inventory_controller = InventoryController(service, view, self.user)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def load_reports(self):
        self.clear_stack()
        self.sidebar.set_active("reports")
        if not self._can_access('reports'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access Reports.")
            return
        
        try:
            db = get_db()
            view = ReportsView()
            service = ReportsService(db)
            self.reports_controller = ReportsController(service, view)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def load_suppliers(self):
        self.clear_stack()
        self.sidebar.set_active("suppliers")
        if not self._can_access('suppliers'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access Suppliers.")
            return
        
        try:
            db = get_db()
            from app.views.SupplierView import SupplierView
            from app.controllers.SupplierController import SupplierController
            
            view = SupplierView()
            service = SupplierService(db)
            self.supplier_controller = SupplierController(service, view)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def load_staff(self):
        self.clear_stack()
        self.sidebar.set_active("staff")
        if not self._can_access('staff'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access Staff.")
            return
        
        try:
            db = get_db()
            from app.views.StaffView import StaffView
            from app.services.StaffService import StaffService
            from app.controllers.StaffController import StaffController
            
            view = StaffView()
            service = StaffService(db)
            self.staff_controller = StaffController(service, view, current_user=self.user)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def load_audit_logs(self):
        self.clear_stack()
        self.sidebar.set_active("audit_logs")
        if not self._can_access('audit_logs'):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to access Audit Logs.")
            return
        
        try:
            from app.views.AuditLogsView import AuditLogsView
            from app.controllers.AuditLogsController import AuditLogsController
            
            db = self.db_connection or get_db()
            view = AuditLogsView(db)
            self.audit_logs_controller = AuditLogsController(db, view)
            
            self.stack.addWidget(view)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel, QMessageBox
            QMessageBox.critical(self, "Database Error", 
                               f"Could not connect to database:\n{str(e)}\n\nPlease check your database connection.")
            label = QLabel(f"Database Error: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            self.stack.addWidget(label)

    def apply_role_permissions(self):
        
        role = self.user.get('role', 'admin')
        
        perms = {
           
            'admin': ['dashboard', 'inventory', 'reports', 'suppliers', 'staff', 'audit_logs'],
          
            'cashier': ['pos']
        }
       
        allowed = perms.get(role, ['pos'])

        self.sidebar.btn_dashboard.setVisible('dashboard' in allowed)
        self.sidebar.btn_pos.setVisible('pos' in allowed)
        self.sidebar.btn_inventory.setVisible('inventory' in allowed)
        self.sidebar.btn_reports.setVisible('reports' in allowed)
        self.sidebar.btn_suppliers.setVisible('suppliers' in allowed)
        self.sidebar.btn_staff.setVisible('staff' in allowed)
        self.sidebar.btn_audit_logs.setVisible('audit_logs' in allowed)

    def _can_access(self, page_key: str) -> bool:
        role = self.user.get('role', 'cashier')
        perms = {
            'admin': ['dashboard', 'inventory', 'reports', 'suppliers', 'staff', 'audit_logs'],
            'cashier': ['pos']
        }
        allowed = perms.get(role, ['pos'])
        return page_key in allowed

    def logout(self):
        try:
            from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
            from app.views.LoginView import LoginView
            from app.services.SecureUserService import SecureUserService
            from app.controllers.LoginController import LoginController
            from app.core.db import get_db

            self.hide()
            db = get_db()
            user_service = SecureUserService(db)
            login_view = LoginView()
            login_controller = LoginController(user_service, login_view)
            
            if login_view.exec() == QDialog.DialogCode.Accepted:
                new_user = login_view.logged_in_user
                if new_user:
                    try:
                        print(f"[MainWindow.logout] Creating new MainWindow for user: {new_user.get('username')} (role: {new_user.get('role')})")
                        new_win = MainWindow(new_user)
                        new_win.show()
                        print("[MainWindow.logout] New MainWindow created and shown successfully")
                        QApplication.instance().logout_new_window = new_win
                    except Exception as e:
                        print(f"[MainWindow.logout ERROR] Failed to create new MainWindow: {e}")
                        import traceback
                        traceback.print_exc()
                        QMessageBox.critical(self, "Error", f"Failed to open main window:\n{str(e)}")
                        self.show()
                        return
                self.close()
            else:
                QApplication.quit()
        except Exception as e:
            print(f"[MainWindow.logout ERROR] {e}")
            import traceback
            traceback.print_exc()
            QApplication.quit()
            traceback.print_exc()
            QMessageBox.critical(self, "Logout Error", f"An error occurred during logout: {e}")