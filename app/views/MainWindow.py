from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QMessageBox, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.views.Sidebar import Sidebar
from app.views.InventoryView import InventoryView
from app.views.POSView import POSView
from app.views.DashboardView import DashboardView
from app.views.ReportsView import ReportsView
from app.models.InventoryModel import InventoryModel
from app.models.SupplierModel import SupplierModel
from app.models.POSModel import POSModel
from app.models.ReportsModel import ReportsModel
from app.controllers.InventoryController import InventoryController
from app.controllers.POSController import POSController
from app.controllers.ReportsController import ReportsController
from app.core.db import get_db

class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        
        self.user = user or {"username": "admin", "role": "admin"}
        self.setWindowTitle("Computer Parts POS System")
        self.resize(1400, 800)
        
        # Load stylesheet
        try:
            with open("app/styles/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass

        # Top-level widget with header + content
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header bar with username and logout
        header_bar = QWidget()
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(16, 10, 16, 10)

        self.lbl_user = QLabel()
        self.lbl_user.setObjectName("header_user")
      
        header_layout.addWidget(self.lbl_user)
        header_layout.addStretch()

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setObjectName("logout_button")
        self.btn_logout.clicked.connect(self.logout)
        header_layout.addWidget(self.btn_logout)

        main_layout.addWidget(header_bar)

        # Main container (sidebar + stack)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        # Apply role-based permissions to sidebar and available pages
        self.apply_role_permissions()

        # Stacked widget for pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        main_layout.addWidget(container)

        self.setCentralWidget(main_widget)

        # Connect sidebar buttons
        self.sidebar.btn_dashboard.clicked.connect(self.load_dashboard)
        self.sidebar.btn_pos.clicked.connect(self.load_pos)
        self.sidebar.btn_inventory.clicked.connect(self.load_inventory)
        self.sidebar.btn_reports.clicked.connect(self.load_reports)
        self.sidebar.btn_suppliers.clicked.connect(self.load_suppliers)
        self.sidebar.btn_staff.clicked.connect(self.load_staff)

        # Load default page based on role permissions
        # Cashiers should start at POS; admins see the dashboard
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
            dashboard = DashboardView(db, self.user)
            # Create controller and keep reference to prevent GC
            from app.controllers.DashboardController import DashboardController
            self.dashboard_controller = DashboardController(dashboard)
            self.stack.addWidget(dashboard)
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
            model = POSModel(db)
            # Pass the authenticated user to POSController so sales are attributed
            self.pos_controller = POSController(model, view, self.user)
            
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
            view = InventoryView(supplier_model=SupplierModel(db))
            model = InventoryModel(db)
            self.inventory_controller = InventoryController(model, view, current_user=self.user)
            
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
            model = ReportsModel()
            self.reports_controller = ReportsController(model, view)
            
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
            from app.models.SupplierModel import SupplierModel
            from app.controllers.SupplierController import SupplierController
            
            view = SupplierView()
            model = SupplierModel(db)
            self.supplier_controller = SupplierController(model, view)
            
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
            from app.models.StaffModel import StaffModel
            from app.controllers.StaffController import StaffController
            
            view = StaffView()
            model = StaffModel(db)
            self.staff_controller = StaffController(model, view)
            
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
        """Enable/disable sidebar buttons based on the logged-in user's role."""
        role = self.user.get('role', 'admin')
        # Define allowed pages per role (only admin and cashier)
        perms = {
            'admin': ['dashboard', 'pos', 'inventory', 'reports', 'suppliers', 'staff'],
            # Cashier should only have access to Point of Sale
            'cashier': ['pos']
        }
        # Default to cashier-like minimal access if role is unknown
        allowed = perms.get(role, ['pos'])

        # Show or hide buttons depending on permissions
        self.sidebar.btn_dashboard.setVisible('dashboard' in allowed)
        self.sidebar.btn_pos.setVisible('pos' in allowed)
        self.sidebar.btn_inventory.setVisible('inventory' in allowed)
        self.sidebar.btn_reports.setVisible('reports' in allowed)
        self.sidebar.btn_suppliers.setVisible('suppliers' in allowed)
        self.sidebar.btn_staff.setVisible('staff' in allowed)

    def _can_access(self, page_key: str) -> bool:
        role = self.user.get('role', 'cashier')
        perms = {
            'admin': ['dashboard', 'pos', 'inventory', 'reports', 'suppliers', 'staff'],
            'cashier': ['pos']
        }
        allowed = perms.get(role, ['pos'])
        return page_key in allowed

    def logout(self):
        """Log out current user: close main window and return to login screen.
        If a new login is accepted, open a fresh MainWindow for that user.
        Otherwise quit the application."""
        try:
            from PyQt6.QtWidgets import QApplication, QDialog
            from app.views.LoginView import LoginView
            from app.models.UserModel import UserModel
            from app.core.db import get_db

            class _Auth:
                def __init__(self, db):
                    self.user_model = UserModel(db)
                def login(self, username, password):
                    return self.user_model.authenticate(username, password)

            # Hide current window and show login dialog
            self.hide()
            auth = _Auth(get_db())
            dlg = LoginView(auth)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                # Open a new MainWindow with the newly authenticated user
                new_user = getattr(dlg, 'user', None)
                if new_user:
                    try:
                        print(f"[MainWindow.logout] Creating new MainWindow for user: {new_user.get('username')} (role: {new_user.get('role')})")
                        new_win = MainWindow(new_user)
                        new_win.show()
                        print("[MainWindow.logout] New MainWindow created and shown successfully")
                        # Keep reference to prevent garbage collection
                        QApplication.instance().logout_new_window = new_win
                    except Exception as e:
                        print(f"[MainWindow.logout ERROR] Failed to create new MainWindow: {e}")
                        import traceback
                        traceback.print_exc()
                        QMessageBox.critical(self, "Error", f"Failed to open main window:\n{str(e)}")
                        self.show()
                        return
                # Close current window instance
                self.close()
            else:
                # If login canceled, quit the whole application
                QApplication.quit()
        except Exception as e:
            print(f"[MainWindow.logout ERROR] {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Logout Error", f"An error occurred during logout: {e}")