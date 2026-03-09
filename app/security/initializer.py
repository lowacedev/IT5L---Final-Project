"""
Security Initialization Module
Initializes all security features on application startup.
"""

import os
from pathlib import Path
from app.security.config import SecurityConfig
from app.security.encryption import get_encryption

class SecurityInitializer:
    """Initializes security features"""
    
    @staticmethod
    def initialize():
        """Initialize all security features"""
        from app.utils.logger import SecurityLogger
        
        print("[SECURITY] Initializing security features...")
        
        # Setup logging
        print("[SECURITY] Setting up logging...")
        SecurityLogger.setup_logging()
        
        # Validate security configuration
        print("[SECURITY] Validating security configuration...")
        try:
            SecurityConfig.validate()
        except ValueError as e:
            logger.critical(f"Security configuration error: {e}")
            raise
        
        # Initialize encryption
        print("[SECURITY] Initializing encryption...")
        try:
            get_encryption()
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.critical(f"Encryption initialization failed: {e}")
            raise
        
        # Create required directories
        print("[SECURITY] Creating required directories...")
        SecurityInitializer._create_directories()
        
        # Verify database connection
        print("[SECURITY] Verifying database connection...")
        try:
            from app.core.db import test_connection
            if test_connection():
                logger.info("Database connection verified")
            else:
                logger.warning("Database connection test failed")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
        
        print("[SECURITY] Security initialization complete!")
        logger.info("Security features initialized successfully")
    
    @staticmethod
    def _create_directories():
        """Create required application directories"""
        directories = [
            Path(SecurityConfig.LOG_FILE).parent,
            Path(SecurityConfig.BACKUP_DIR),
            Path("app/security"),
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                logger.warning(f"Could not create directory {directory}: {e}")


# Run initialization
if __name__ == "__main__":
    SecurityInitializer.initialize()
