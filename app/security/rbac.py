"""
Role-Based Access Control (RBAC) Module
Manages user roles, permissions, and access control.
"""

from typing import List, Set, Dict, Optional
from enum import Enum
from dataclasses import dataclass

class UserRole(Enum):
    """Available user roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"


@dataclass
class Permission:
    """Permission definition"""
    name: str
    description: str
    resource: str
    action: str
    
    def __hash__(self):
        return hash((self.name, self.resource, self.action))


class RBACManager:
    """Manages role-based access control"""
    
    # Define permissions for each role
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.ADMIN: {
            # User Management
            Permission("manage_users", "Create, edit, delete users", "users", "manage"),
            Permission("view_users", "View all users", "users", "read"),
            Permission("reset_password", "Reset user passwords", "users", "reset_password"),
            Permission("manage_roles", "Assign and modify user roles", "users", "manage_roles"),
            
            # Inventory Management
            Permission("manage_inventory", "Create, edit, delete inventory items", "inventory", "manage"),
            Permission("view_inventory", "View inventory", "inventory", "read"),
            Permission("adjust_stock", "Adjust inventory stock", "inventory", "adjust_stock"),
            
            # Sales
            Permission("view_all_sales", "View all sales", "sales", "read_all"),
            Permission("delete_sales", "Delete sales transactions", "sales", "delete"),
            
            # Reports
            Permission("view_reports", "View reports", "reports", "read"),
            Permission("export_reports", "Export reports", "reports", "export"),
            
            # System
            Permission("view_logs", "View system logs", "logs", "read"),
            Permission("manage_settings", "System configuration", "settings", "manage"),
            Permission("database_backup", "Create database backups", "database", "backup"),
            Permission("user_audit", "View user audit logs", "audit", "read"),
        },
        
        UserRole.MANAGER: {
            # Inventory
            Permission("manage_inventory", "Create, edit inventory", "inventory", "manage"),
            Permission("view_inventory", "View inventory", "inventory", "read"),
            Permission("adjust_stock", "Adjust inventory stock", "inventory", "adjust_stock"),
            
            # Sales
            Permission("view_all_sales", "View all sales", "sales", "read_all"),
            
            # Reports
            Permission("view_reports", "View reports", "reports", "read"),
            
            # Users (limited)
            Permission("view_users", "View users", "users", "read"),
            Permission("reset_password", "Reset user passwords", "users", "reset_password"),
        },
        
        UserRole.CASHIER: {
            # Sales
            Permission("create_sale", "Create sales transactions", "sales", "create"),
            Permission("view_own_sales", "View own sales", "sales", "read_own"),
            Permission("refund_sale", "Refund sales", "sales", "refund"),
            
            # Inventory (read-only)
            Permission("view_inventory", "View inventory", "inventory", "read"),
        },
    }
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> Set[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role (UserRole): User role
            
        Returns:
            Set[Permission]: Set of permissions
        """
        return RBACManager.ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(user_role: UserRole, permission_name: str) -> bool:
        """
        Check if role has specific permission.
        
        Args:
            user_role (UserRole): User role
            permission_name (str): Permission name
            
        Returns:
            bool: True if has permission
        """
        permissions = RBACManager.get_role_permissions(user_role)
        return any(p.name == permission_name for p in permissions)
    
    @staticmethod
    def has_resource_action(user_role: UserRole, resource: str, action: str) -> bool:
        """
        Check if role can perform action on resource.
        
        Args:
            user_role (UserRole): User role
            resource (str): Resource name
            action (str): Action name
            
        Returns:
            bool: True if allowed
        """
        permissions = RBACManager.get_role_permissions(user_role)
        return any(p.resource == resource and p.action == action for p in permissions)
    
    @staticmethod
    def can_access_feature(user_role: UserRole, feature: str) -> bool:
        """
        Check if user can access a GUI feature.
        
        Args:
            user_role (UserRole): User role
            feature (str): Feature name
            
        Returns:
            bool: True if can access
        """
        feature_permissions = {
            "user_management": "manage_users",
            "inventory_management": "manage_inventory",
            "sales_management": "create_sale",
            "reports": "view_reports",
            "system_logs": "view_logs",
            "settings": "manage_settings",
        }
        
        required_permission = feature_permissions.get(feature)
        if not required_permission:
            return True  # Unknown features are accessible by default
        
        return RBACManager.has_permission(user_role, required_permission)
    
    @staticmethod
    def get_accessible_features(user_role: UserRole) -> List[str]:
        """
        Get all features accessible by a role.
        
        Args:
            user_role (UserRole): User role
            
        Returns:
            List[str]: List of accessible features
        """
        feature_permissions = {
            "user_management": "manage_users",
            "inventory_management": "manage_inventory",
            "sales_management": "create_sale",
            "reports": "view_reports",
            "system_logs": "view_logs",
            "settings": "manage_settings",
        }
        
        accessible = []
        for feature, permission in feature_permissions.items():
            if RBACManager.has_permission(user_role, permission):
                accessible.append(feature)
        
        return accessible


class SessionManager:
    """Manages user sessions with role information"""
    
    def __init__(self):
        self.current_user = None
        self.current_role = None
        self.login_time = None
    
    def start_session(self, user_id: int, username: str, role: str, login_time=None):
        """Start user session"""
        try:
            self.current_user = {
                'id': user_id,
                'username': username,
            }
            self.current_role = UserRole(role)
            self.login_time = login_time or __import__('datetime').datetime.now()
            
            logger.info(f"Session started for user: {username} with role: {role}")
        except ValueError:
            logger.error(f"Invalid role: {role}")
            raise
    
    def end_session(self):
        """End user session"""
        if self.current_user:
            logger.info(f"Session ended for user: {self.current_user['username']}")
        
        self.current_user = None
        self.current_role = None
        self.login_time = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None and self.current_role is not None
    
    def can_perform_action(self, resource: str, action: str) -> bool:
        """Check if current user can perform action"""
        if not self.is_authenticated():
            return False
        
        has_access = RBACManager.has_resource_action(self.current_role, resource, action)
        
        if not has_access:
            SecurityAuditLogger.log_unauthorized_access_attempt(
                self.current_user['username'],
                resource,
                action
            )
        
        return has_access
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if current user can access feature"""
        if not self.is_authenticated():
            return False
        
        return RBACManager.can_access_feature(self.current_role, feature)
    
    def get_accessible_features(self) -> List[str]:
        """Get all accessible features for current user"""
        if not self.is_authenticated():
            return []
        
        return RBACManager.get_accessible_features(self.current_role)
    
    def get_username(self) -> Optional[str]:
        """Get current username"""
        return self.current_user['username'] if self.current_user else None
    
    def get_role(self) -> Optional[UserRole]:
        """Get current user role"""
        return self.current_role


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get or create session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Example usage
if __name__ == "__main__":
    # Test RBAC
    print("=== Admin Permissions ===")
    admin_perms = RBACManager.get_role_permissions(UserRole.ADMIN)
    for perm in admin_perms:
        print(f"- {perm.name}: {perm.description}")
    
    print("\n=== Cashier Permissions ===")
    cashier_perms = RBACManager.get_role_permissions(UserRole.CASHIER)
    for perm in cashier_perms:
        print(f"- {perm.name}: {perm.description}")
    
    # Test session
    print("\n=== Session Test ===")
    session = get_session_manager()
    session.start_session(1, "admin_user", "admin")
    
    print(f"Username: {session.get_username()}")
    print(f"Role: {session.get_role().value}")
    print(f"Can manage users: {session.can_perform_action('users', 'manage')}")
    print(f"Can delete sales: {session.can_perform_action('sales', 'delete')}")
    print(f"Accessible features: {session.get_accessible_features()}")
