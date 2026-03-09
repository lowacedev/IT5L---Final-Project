"""
Backup Manager
Handles database backups and logs them to the backup_logs table.
"""

import os
import subprocess
import datetime
from pathlib import Path
from typing import Optional
from app.security.config import SecurityConfig
from app.utils.logger import get_logger, SecurityAuditLogger

logger = get_logger(__name__)


class BackupManager:
    """Manages database backups and logging"""
    
    @staticmethod
    def create_backup(backup_path: str = None, db_connection=None) -> dict:
        """
        Create a database backup and log it.
        
        Args:
            backup_path: Custom path for backup file (optional)
            db_connection: Database connection for logging
            
        Returns:
            dict: Backup result with success status and details
        """
        try:
            # Generate backup filename if not provided
            if backup_path is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path(SecurityConfig.BACKUP_DIR)
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = str(backup_dir / f"{SecurityConfig.DB_NAME}_{timestamp}.sql")
            
            # Ensure backup directory exists
            backup_dir = Path(backup_path).parent
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting database backup to {backup_path}")
            
            # Build mysqldump command
            cmd = [
                "mysqldump",
                f"--host={SecurityConfig.DB_HOST}",
                f"--user={SecurityConfig.DB_USER}",
                f"--password={SecurityConfig.DB_PASSWORD}",
                "--single-transaction",
                "--routines",
                "--triggers",
                SecurityConfig.DB_NAME
            ]
            
            # Execute backup
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr
                logger.error(f"Backup failed: {error_msg}")
                BackupManager._log_backup_to_db(
                    db_connection,
                    backup_path=backup_path,
                    backup_size=0,
                    success=False,
                    error_message=error_msg
                )
                return {
                    'success': False,
                    'message': f'Backup failed: {error_msg}',
                    'backup_path': None
                }
            
            # Get backup file size
            backup_size = os.path.getsize(backup_path)
            logger.info(f"Backup completed successfully. Size: {backup_size / (1024*1024):.2f} MB")
            
            # Log to database
            BackupManager._log_backup_to_db(
                db_connection,
                backup_path=backup_path,
                backup_size=backup_size,
                success=True,
                error_message=None
            )
            
            # Log to audit logger
            SecurityAuditLogger.log_user_action(
                'system',
                'backup_created',
                f'Database backup created: {os.path.basename(backup_path)} ({backup_size / (1024*1024):.2f} MB)'
            )
            
            return {
                'success': True,
                'message': f'Backup created successfully at {backup_path}',
                'backup_path': backup_path,
                'backup_size': backup_size
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Backup error: {error_msg}")
            SecurityAuditLogger.log_system_error("BACKUP_ERROR", error_msg)
            return {
                'success': False,
                'message': f'Backup error: {error_msg}',
                'backup_path': None
            }
    
    @staticmethod
    def restore_backup(backup_file: str, db_connection=None) -> dict:
        """
        Restore database from backup file.
        
        Args:
            backup_file: Path to backup SQL file
            db_connection: Database connection for logging
            
        Returns:
            dict: Restore result with success status
        """
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Check file size
            file_size = os.path.getsize(backup_file)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"Starting database restore from {backup_file} ({file_size_mb:.2f} MB)")
            
            # Build mysql command with optimizations for faster restore
            cmd = [
                "mysql",
                f"--host={SecurityConfig.DB_HOST}",
                f"--user={SecurityConfig.DB_USER}",
                f"--password={SecurityConfig.DB_PASSWORD}",
                "--max_allowed_packet=1024M",
                "-v",  # Verbose to show progress
                SecurityConfig.DB_NAME
            ]
            
            # Execute restore with proper error handling and performance optimizations
            with open(backup_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd, 
                    stdin=f, 
                    stderr=subprocess.PIPE, 
                    stdout=subprocess.PIPE,
                    text=True,
                    timeout=3600  # 1 hour timeout for large restores
                )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Restore failed: {error_msg}")
                BackupManager._log_restore_to_db(
                    db_connection,
                    backup_file=backup_file,
                    success=False,
                    error_message=error_msg
                )
                return {
                    'success': False,
                    'message': f'Restore failed: {error_msg}'
                }
            
            logger.info(f"Database restore completed successfully from {backup_file}")
            
            # Log to database
            BackupManager._log_restore_to_db(
                db_connection,
                backup_file=backup_file,
                success=True,
                error_message=None
            )
            
            # Log to audit logger
            SecurityAuditLogger.log_user_action(
                'system',
                'backup_restored',
                f'Database restored from: {os.path.basename(backup_file)} ({file_size_mb:.2f} MB)'
            )
            
            return {
                'success': True,
                'message': 'Database restored successfully'
            }
            
        except subprocess.TimeoutExpired:
            error_msg = "Restore exceeded 1 hour timeout - may still be processing"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Restore error: {error_msg}")
            SecurityAuditLogger.log_system_error("RESTORE_ERROR", error_msg)
            return {
                'success': False,
                'message': f'Restore error: {error_msg}'
            }
    
    @staticmethod
    def _log_backup_to_db(db_connection, backup_path: str, backup_size: int, success: bool, error_message: Optional[str] = None):
        """Log backup operation to database"""
        if not db_connection:
            return
        
        try:
            cursor = db_connection.cursor()
            
            query = """
                INSERT INTO backup_logs (backup_file, backup_size, success, error_message)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                backup_path,
                backup_size,
                success,
                error_message
            ))
            
            db_connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Failed to log backup to database: {str(e)}")
    
    @staticmethod
    def _log_restore_to_db(db_connection, backup_file: str, success: bool, error_message: Optional[str] = None):
        """Log restore operation to database"""
        if not db_connection:
            return
        
        try:
            cursor = db_connection.cursor()
            
            query = """
                UPDATE backup_logs
                SET restored_from = %s, success = %s, error_message = %s
                WHERE id = (SELECT MAX(id) FROM backup_logs)
            """
            
            cursor.execute(query, (
                backup_file,
                success,
                error_message
            ))
            
            db_connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Failed to log restore to database: {str(e)}")
    
    @staticmethod
    def list_backups() -> list:
        """
        List all available backup files.
        
        Returns:
            list: List of backup file info dicts with name, size, timestamp
        """
        try:
            backup_dir = Path(SecurityConfig.BACKUP_DIR)
            backups = []
            
            if not backup_dir.exists():
                return backups
            
            # Get all SQL files in backup directory
            for backup_file in sorted(backup_dir.glob("*.sql"), reverse=True):
                try:
                    file_size = backup_file.stat().st_size
                    file_mtime = backup_file.stat().st_mtime
                    
                    backups.append({
                        'name': backup_file.name,
                        'path': str(backup_file),
                        'size': file_size,
                        'size_mb': file_size / (1024 * 1024),
                        'timestamp': datetime.datetime.fromtimestamp(file_mtime)
                    })
                except Exception as e:
                    logger.error(f"Error reading backup file {backup_file}: {str(e)}")
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    @staticmethod
    def delete_backup(backup_path: str) -> dict:
        """
        Delete a backup file.
        
        Args:
            backup_path: Path to backup file to delete
            
        Returns:
            dict: Result with success status
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return {'success': False, 'message': 'Backup file not found'}
            
            backup_file.unlink()
            logger.info(f"Backup deleted: {backup_path}")
            
            return {
                'success': True,
                'message': f'Backup {backup_file.name} deleted successfully'
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to delete backup: {error_msg}")
            return {
                'success': False,
                'message': f'Failed to delete backup: {error_msg}'
            }
