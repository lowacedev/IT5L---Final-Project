"""
Global signals for inter-component communication.
This module centralizes signal definitions to ensure they're available
to all component regardless of import order.
"""

from PyQt6.QtCore import pyqtSignal, QObject


class AuditLogSignals(QObject):
    """Signals for audit log updates across the application"""
    logs_updated = pyqtSignal()  # Emitted whenever an audit log entry is created


# Global signal instance - guaranteed to exist regardless of import order
audit_log_signals = AuditLogSignals()
