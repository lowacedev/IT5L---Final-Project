"""
Database Query Timeout Handler
Prevents database queries from hanging indefinitely.
"""

import threading
from functools import wraps
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DBQueryTimeout:
    """Wraps database operations with timeout support"""
    
    @staticmethod
    def execute_with_timeout(func, timeout_seconds=10):
        """
        Execute database function with timeout.
        
        Args:
            func: Function to execute
            timeout_seconds: Timeout in seconds (default 10)
            
        Returns:
            Result of function call or None if timeout
        """
        result = [None]
        exception = [None]
        
        def wrapper():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        if thread.is_alive():
            logger.warning(f"Database operation timed out after {timeout_seconds} seconds")
            return None
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    @staticmethod
    def query_timeout(timeout_seconds=10):
        """
        Decorator to add timeout to database query methods.
        
        Args:
            timeout_seconds: Timeout in seconds
            
        Usage:
            @query_timeout(10)
            def my_database_query(self):
                ...
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return DBQueryTimeout.execute_with_timeout(
                        lambda: func(*args, **kwargs),
                        timeout_seconds
                    )
                except Exception as e:
                    logger.error(f"Database query error: {str(e)}")
                    raise
            return wrapper
        return decorator
