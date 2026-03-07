"""
Security Configuration Module
Loads and manages all security-related settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
ENV_PATH = Path(__file__).parent.parent.parent / '.env'
load_dotenv(ENV_PATH)

class SecurityConfig:
    """Central security configuration"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'computerparts_pos')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not found in .env file. Please set it.")
    
    # Password Policy
    MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', '8'))
    REQUIRE_SPECIAL_CHARS = os.getenv('REQUIRE_SPECIAL_CHARS', 'true').lower() == 'true'
    REQUIRE_NUMBERS = os.getenv('REQUIRE_NUMBERS', 'true').lower() == 'true'
    REQUIRE_UPPERCASE = os.getenv('REQUIRE_UPPERCASE', 'true').lower() == 'true'
    
    # Login Security
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOGIN_LOCKOUT_DURATION = int(os.getenv('LOGIN_LOCKOUT_DURATION', '900'))  # seconds
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Backup
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
    BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups/')
    
    # Debug
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @staticmethod
    def validate():
        """Validate critical security settings"""
        if not SecurityConfig.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not configured!")
        if len(SecurityConfig.ENCRYPTION_KEY) < 32:
            raise ValueError("ENCRYPTION_KEY must be at least 32 characters!")
        if SecurityConfig.DB_PASSWORD == '':
            print("[WARNING] Database password is empty!")
