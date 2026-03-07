"""
Centralized Logging Module
Handles all application logging to file and database.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from app.security.config import SecurityConfig

class SecurityLogger:
    """Centralized logger for application"""
    
    _loggers = {}
    _db_handler = None
    
    @staticmethod
    def setup_logging(db_connection=None):
        """
        Setup logging configuration.
        
        Args:
            db_connection: Optional database connection for database logging
        """
        # Create logs directory if it doesn't exist
        log_dir = Path(SecurityConfig.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, SecurityConfig.LOG_LEVEL))
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            SecurityConfig.LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Add database logging handler if connection provided
        if db_connection:
            try:
                from app.utils.DatabaseLoggingHandler import DatabaseLoggingHandler
                db_handler = DatabaseLoggingHandler(db_connection)
                db_handler.setFormatter(formatter)
                root_logger.addHandler(db_handler)
                SecurityLogger._db_handler = db_handler
            except Exception as e:
                # Log to file only if database handler fails
                logging.warning(f"Database logging not available: {str(e)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get or create logger instance.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    if name not in SecurityLogger._loggers:
        SecurityLogger._loggers[name] = logging.getLogger(name)
    return SecurityLogger._loggers[name]


class SecurityAuditLogger:
    """Audit logger for security-related events"""
    
    @staticmethod
    def log_login_attempt(username: str, success: bool, ip_address: str = None, reason: str = None):
        """Log login attempt"""
        logger = get_logger('SECURITY.AUTH')
        status = "SUCCESS" if success else "FAILED"
        message = f"Login attempt [{status}] - Username: {username}"
        if ip_address:
            message += f" - IP: {ip_address}"
        if reason:
            message += f" - Reason: {reason}"
        
        if success:
            logger.info(message)
        else:
            logger.warning(message)
    
    @staticmethod
    def log_account_lockout(username: str, reason: str = "Max login attempts exceeded"):
        """Log account lockout"""
        logger = get_logger('SECURITY.AUTH')
        logger.critical(f"Account locked - Username: {username} - Reason: {reason}")
    
    @staticmethod
    def log_account_unlock(username: str):
        """Log account unlock"""
        logger = get_logger('SECURITY.AUTH')
        logger.info(f"Account unlocked - Username: {username}")
    
    @staticmethod
    def log_password_change(username: str, success: bool):
        """Log password change"""
        logger = get_logger('SECURITY.AUTH')
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Password change [{status}] - Username: {username}")
    
    @staticmethod
    def log_unauthorized_access_attempt(user: str, resource: str, action: str):
        """Log unauthorized access attempt"""
        logger = get_logger('SECURITY.AUTHORIZATION')
        logger.warning(f"Unauthorized access attempt - User: {user} - Resource: {resource} - Action: {action}")
    
    @staticmethod
    def log_user_action(user: str, action: str, details: str = None):
        """Log user action"""
        logger = get_logger('SECURITY.AUDIT')
        message = f"User action - User: {user} - Action: {action}"
        if details:
            message += f" - Details: {details}"
        logger.info(message)
    
    @staticmethod
    def log_data_access(user: str, resource: str, access_type: str):
        """Log data access"""
        logger = get_logger('SECURITY.DATA_ACCESS')
        logger.info(f"Data access - User: {user} - Resource: {resource} - Type: {access_type}")
    
    @staticmethod
    def log_system_error(error_type: str, error_message: str, user: str = None):
        """Log system error"""
        logger = get_logger('SECURITY.ERROR')
        message = f"System error - Type: {error_type}"
        if user:
            message += f" - User: {user}"
        message += f" - Message: {error_message[:100]}"  # Truncate long messages
        logger.error(message)
    
    @staticmethod
    def log_database_operation(user: str, operation: str, table: str, success: bool):
        """Log database operation"""
        logger = get_logger('SECURITY.DATABASE')
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"DB operation [{status}] - User: {user} - Operation: {operation} - Table: {table}")
    
    @staticmethod
    def log_encryption_operation(operation: str, success: bool, details: str = None):
        """Log encryption operation"""
        logger = get_logger('SECURITY.ENCRYPTION')
        status = "SUCCESS" if success else "FAILED"
        message = f"Encryption operation [{status}] - Operation: {operation}"
        if details:
            message += f" - {details}"
        logger.info(message)

# Initialize logging on module import (file-based only, database added later)
SecurityLogger.setup_logging()


# Example usage
if __name__ == "__main__":
    # Setup logging
    SecurityLogger.setup_logging()
    
    # Get logger
    logger = get_logger(__name__)
    
    # Test logging
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test audit logging
    SecurityAuditLogger.log_login_attempt("admin", True, "192.168.1.1")
    SecurityAuditLogger.log_user_action("admin", "Create user", "Created user: john")
    SecurityAuditLogger.log_data_access("admin", "sales", "READ")
