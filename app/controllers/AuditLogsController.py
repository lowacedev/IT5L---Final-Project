"""
Audit Logs Controller
Manages interactions between AuditLogsView and data services.
"""

from app.views.AuditLogsView import AuditLogsView
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuditLogsController:
    """Controller for audit logs view"""
    
    def __init__(self, db_connection, parent_view=None):
        """
        Initialize controller.
        
        Args:
            db_connection: Database connection
            parent_view: Parent widget
        """
        self.db_connection = db_connection
        self.parent_view = parent_view
        self.view = None
    
    def show_audit_logs(self):
        """Show audit logs view"""
        try:
            self.view = AuditLogsView(self.db_connection)
            logger.info("Audit logs view opened")
            return self.view
        except Exception as e:
            logger.error(f"Failed to open audit logs: {str(e)}")
            raise
