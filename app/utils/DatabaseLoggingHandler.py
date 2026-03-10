"""
Database Logging Handler
Integrates Python logging with MySQL database for persistent log storage.
Allows real-time log monitoring and querying.
"""

import logging
import threading
from datetime import datetime
from queue import Queue
from typing import Optional, Dict, Any, Union


class DatabaseLoggingHandler(logging.Handler):
    """Custom logging handler that writes logs to database"""
    
    def __init__(self, db_connection=None, queue_size: int = 1000):
        """
        Initialize database logging handler.
        
        Args:
            db_connection: Database connection object (for config/validation only)
            queue_size: Size of the log queue for buffering
        """
        super().__init__()
        self.db_connection = None  # Will create separate connection for logging
        self.log_queue = Queue(maxsize=queue_size)
        self.stop_event = threading.Event()
        self._init_lock = threading.Lock()
        
        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to database via queue.
        Only logs INFO and above to reduce noise in audit logs.
        
        Args:
            record: LogRecord to emit
        """
        try:
            # Filter out DEBUG level logs to reduce database noise
            if record.levelno < logging.INFO:
                return
            
            # Parse log context
            log_data = self._parse_record(record)
            
            # Queue the log for async processing
            if not self.log_queue.full():
                self.log_queue.put(log_data, block=False)
        except Exception:
            self.handleError(record)
    
    def _parse_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Parse log record into structured data.
        
        Args:
            record: LogRecord to parse
            
        Returns:
            Dict with parsed log data
        """
        full_message = self.format(record)
        
        # Extract context from logger name (e.g., "SECURITY.AUTH")
        logger_name = record.name
        parts = logger_name.split('.')
        
        event_type = parts[-1].upper() if len(parts) > 0 else "SYSTEM"
        module = parts[0] if len(parts) > 0 else "APP"
        
        # Remove timestamp from message for details (avoid duplication)
        message = self._remove_timestamp_prefix(full_message)
        
        # Extract structured fields from message
        username = self._extract_field(message, "Username")
        user_id = self._extract_field(message, "UserId", is_int=True)
        action = self._extract_action(message)
        reason = self._extract_field(message, "Reason")
        
        return {
            'event_type': event_type,
            'module': module,
            'level': record.levelname,
            'message': message,
            'username': username,
            'user_id': user_id,
            'action': action,
            'reason': reason,
            'timestamp': datetime.fromtimestamp(record.created)
        }
    
    def _remove_timestamp_prefix(self, message: str) -> str:
        """
        Extract only the message content, removing timestamp, level, and location.
        
        Pattern: [YYYY-MM-DD HH:MM:SS] LEVEL [module:line] - MESSAGE
        Result: MESSAGE only
        
        Args:
            message: Formatted log message
            
        Returns:
            Message content only
        """
        try:
            import re
            # Remove: [timestamp] LEVEL [location] - 
            # Keeps: the actual message after the dash
            pattern = r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s+\w+\s+\[.*?\]\s*-\s*'
            cleaned = re.sub(pattern, '', message)
            
            # Also handle case where timestamp was already removed by format
            if cleaned == message:
                # Try pattern without timestamp
                pattern2 = r'^\w+\s+\[.*?\]\s*-\s*'
                cleaned = re.sub(pattern2, '', message)
            
            return cleaned if cleaned else message
        except Exception:
            return message
    
    def _extract_resource(self, message: str, event_type: str) -> Optional[str]:
        """
        Extract resource being accessed.
        
        Args:
            message: Log message
            event_type: Type of event
            
        Returns:
            Resource name (table/module being accessed)
        """
        # Try explicit Resource field first
        resource = self._extract_field(message, "Resource")
        if resource:
            return resource
        
        # Infer resource from message content
        resource_mappings = {
            'suppliers': ['supplier', 'suppliers'],
            'staff': ['staff', 'employee'],
            'inventory': ['inventory', 'product', 'stock'],
            'sales': ['sale', 'sales', 'checkout', 'pos'],
            'users': ['user', 'account', 'password'],
            'database': ['database', 'connection', 'db'],
        }
        
        message_lower = message.lower()
        for resource_type, keywords in resource_mappings.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return resource_type
        
        # System logs don't have resources
        if event_type in ['DB', 'ENCRYPTION', 'ERROR']:
            return None
        
        return None
    
    def _extract_action(self, message: str) -> Optional[str]:
        """
        Extract action being performed.
        
        Args:
            message: Log message
            
        Returns:
            Action name (create, update, delete, login, etc.)
        """
        # Try explicit Action field first
        action = self._extract_field(message, "Action")
        if action:
            return action
        
        # Infer action from message content
        action_keywords = {
            'CREATE': ['created', 'create', 'added', 'add'],
            'UPDATE': ['updated', 'update', 'modified', 'modify'],
            'DELETE': ['deleted', 'delete', 'removed', 'remove'],
            'LOGIN': ['login', 'logged in'],
            'LOGOUT': ['logout', 'logged out'],
            'READ': ['retrieved', 'fetched', 'queried'],
            'ENCRYPT': ['encrypted', 'encrypt'],
            'DECRYPT': ['decrypted', 'decrypt'],
            'VALIDATE': ['validated', 'validate'],
        }
        
        message_lower = message.lower()
        for action_type, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return action_type
        
        return None
    
    def _extract_field(self, message: str, field_name: str, is_int: bool = False) -> Optional[Union[int, str]]:
        """
        Extract field value from log message.
        
        Args:
            message: Log message
            field_name: Field name to extract
            is_int: Convert to int if True
            
        Returns:
            Extracted value (int or str) or None
        """
        try:
            if field_name in message:
                start = message.find(field_name) + len(field_name)
                start = message.find(':', start) + 1 if ':' in message[start:start+20] else start
                
                # Find end of value
                end_chars = [' - ', '\n', '\t']
                end = len(message)
                for char_seq in end_chars:
                    pos = message.find(char_seq, start)
                    if pos != -1 and pos < end:
                        end = pos
                
                value = message[start:end].strip()
                if is_int and value.isdigit():
                    return int(value)
                return value if value else None
        except Exception:
            pass
        return None
    
    def _extract_clean_details(self, message: str) -> str:
        """
        Extract only the meaningful details part from message, removing redundant fields.
        For messages like: "Username: armel - UserId: 23 - Created item: X"
        Returns: "Created item: X"
        
        Args:
            message: Full log message
            
        Returns:
            Clean details message
        """
        try:
            # Find the last " - " which separates UserId from actual details
            if "UserId:" in message:
                # Find position after "UserId: NN - "
                userid_pos = message.find("UserId:")
                if userid_pos != -1:
                    # Find the " - " after UserId value
                    dash_pos = message.find(" - ", userid_pos)
                    if dash_pos != -1:
                        # Return everything after this dash
                        return message[dash_pos + 3:]
            # Fallback: if no UserId, look for the last " - "
            dash_pos = message.rfind(" - ")
            if dash_pos != -1:
                return message[dash_pos + 3:]
            # Final fallback: return whole message
            return message
        except Exception:
            return message
    
    def _process_logs(self) -> None:
        """Process queued logs and write to database"""
        import time
        
        while not self.stop_event.is_set():
            try:
                # Try to get log from queue with SHORT timeout (100ms) for responsive processing
                log_data = self.log_queue.get(timeout=0.1)
                self._write_to_database(log_data)
                
            except Exception:
                # Queue timeout - try again immediately
                time.sleep(0.05)  # Small sleep to prevent busy-waiting
    
    def _write_to_database(self, log_data: Dict[str, Any]) -> None:
        """
        Write log data to appropriate database table.
        Uses a separate database connection to avoid thread-safety issues.
        
        Args:
            log_data: Log data dictionary
        """
        try:
            # Create a separate connection for logging (thread-safe)
            from app.core.db import get_db
            db_connection = get_db()
            cursor = db_connection.cursor()
            
            event_type = log_data['event_type']
            
            # Determine table and write accordingly
            if event_type == 'AUTH':
                self._write_auth_log(cursor, log_data)
            elif event_type == 'AUTHORIZATION':
                self._write_access_control_log(cursor, log_data)
            elif event_type == 'AUDIT':
                self._write_user_activity_log(cursor, log_data)
            elif event_type == 'DATA_ACCESS':
                self._write_data_access_log(cursor, log_data)
            else:
                self._write_general_audit_log(cursor, log_data)
            
            db_connection.commit()
            cursor.close()
            db_connection.close()
            
        except Exception as e:
            # Silently fail - logging should never crash the app
            try:
                import sys
                print(f"[WARNING] Database logging failed: {str(e)}", file=sys.stderr)
            except Exception:
                pass
    
    def _write_auth_log(self, cursor, log_data: Dict[str, Any]) -> None:
        """Write authentication log"""
        status = "SUCCESS" if "SUCCESS" in log_data['message'] else "FAILED"
        
        # Handle case where user_id might be None
        if log_data.get('user_id'):
            sql = """
            INSERT INTO security_audit_logs 
            (event_type, username, user_id, action, status, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                'AUTH',
                log_data['username'],
                log_data['user_id'],
                'LOGIN',
                status,
                log_data['message'],
                log_data['timestamp']
            ))
        else:
            sql = """
            INSERT INTO security_audit_logs 
            (event_type, username, action, status, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                'AUTH',
                log_data['username'],
                'LOGIN',
                status,
                log_data['message'],
                log_data['timestamp']
            ))
    
    def _write_access_control_log(self, cursor, log_data: Dict[str, Any]) -> None:
        """Write access control log with optional user_id"""
        allowed = "DENIED" not in log_data['message']
        
        # Handle case where user_id might be None - fallback to general audit log
        if not log_data.get('user_id'):
            self._write_general_audit_log(cursor, log_data)
            return
        
        sql = """
        INSERT INTO access_control_logs
        (username, user_id, resource, action, allowed, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            log_data['username'],
            log_data['user_id'],
            log_data.get('resource'),
            log_data['action'],
            allowed,
            log_data['timestamp']
        ))
    
    def _write_user_activity_log(self, cursor, log_data: Dict[str, Any]) -> None:
        """Write user activity log to both user_activity_logs and security_audit_logs"""
        # If user_id is not available, write to general audit log instead
        if not log_data.get('user_id'):
            self._write_general_audit_log(cursor, log_data)
            return
        
        # Extract clean details (remove redundant username/userid info from message)
        clean_details = self._extract_clean_details(log_data['message'])
        
        # Write to user_activity_logs table
        sql = """
        INSERT INTO user_activity_logs
        (username, user_id, action, module, details, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            log_data['username'],
            log_data['user_id'],
            log_data['action'],
            log_data['module'],
            clean_details,
            log_data['timestamp']
        ))
        
        # Also write to security_audit_logs for comprehensive audit trail
        audit_sql = """
        INSERT INTO security_audit_logs
        (event_type, username, user_id, action, details, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(audit_sql, (
            log_data['module'],  # Use module as event_type (e.g., INVENTORY, STAFF, SUPPLIER, POS)
            log_data['username'],
            log_data['user_id'],
            log_data['action'],
            clean_details,
            log_data['timestamp']
        ))
    
    def _write_data_access_log(self, cursor, log_data: Dict[str, Any]) -> None:
        """Write data access log with optional user_id"""
        # Handle case where user_id might be None
        if log_data.get('user_id'):
            sql = """
            INSERT INTO security_audit_logs
            (event_type, username, user_id, resource, action, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                'DATA_ACCESS',
                log_data['username'],
                log_data['user_id'],
                log_data.get('resource'),
                log_data['action'],
                log_data['message'],
                log_data['timestamp']
            ))
        else:
            sql = """
            INSERT INTO security_audit_logs
            (event_type, username, resource, action, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                'DATA_ACCESS',
                log_data['username'],
                log_data.get('resource'),
                log_data['action'],
                log_data['message'],
                log_data['timestamp']
            ))
    
    def _write_general_audit_log(self, cursor, log_data: Dict[str, Any]) -> None:
        """Write general audit log with optional user_id"""
        status = "SUCCESS" if log_data['level'] in ['INFO', 'DEBUG'] else "FAILED"
        
        # Handle case where user_id might be None - log without it
        if log_data.get('user_id'):
            sql = """
            INSERT INTO security_audit_logs
            (event_type, username, user_id, action, status, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                log_data['event_type'],
                log_data['username'],
                log_data['user_id'],
                log_data['action'],
                status,
                log_data['message'],
                log_data['timestamp']
            ))
        else:
            sql = """
            INSERT INTO security_audit_logs
            (event_type, username, action, status, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                log_data['event_type'],
                log_data['username'],
                log_data['action'],
                status,
                log_data['message'],
                log_data['timestamp']
            ))
    
    def close(self) -> None:
        """Close handler and wait for queue to drain"""
        self.stop_event.set()
        
        # Process remaining logs
        while not self.log_queue.empty():
            try:
                log_data = self.log_queue.get_nowait()
                self._write_to_database(log_data)
            except Exception:
                break
        
        # Wait for worker thread
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        super().close()
