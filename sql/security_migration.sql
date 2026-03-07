-- Database Schema Updates for Security
-- Run these migrations to add security features to existing database

USE computerparts_pos;

-- Update users table to support secure authentication
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT 1;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_attempt TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_ip VARCHAR(45) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS require_password_change BOOLEAN DEFAULT 0;

-- Create audit log table for security events
CREATE TABLE IF NOT EXISTS security_audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- LOGIN, LOGOUT, FAILED_LOGIN, DATA_ACCESS, etc.
    username VARCHAR(50),
    user_id INT,
    resource VARCHAR(100),
    action VARCHAR(100),
    ip_address VARCHAR(45),
    status VARCHAR(20), -- SUCCESS, FAILED
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_username (username)
);

-- Create session table for managing user sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
);

-- Create table for storing encrypted customer data
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS phone_encrypted VARCHAR(255) NULL;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS email_encrypted VARCHAR(255) NULL;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS data_encrypted BOOLEAN DEFAULT 0;

-- Create table for login attempt tracking
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    ip_address VARCHAR(45),
    reason VARCHAR(255),
    INDEX idx_username_time (username, attempt_time)
);

-- Add check constraint for roles (ensure only valid roles are stored)
-- Note: ENUM already enforces this, but document it here

-- Create activity log for user actions
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50),
    action VARCHAR(100),
    module VARCHAR(50),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_action (action)
);

-- Create access control logs
CREATE TABLE IF NOT EXISTS access_control_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50),
    resource VARCHAR(100),
    action VARCHAR(100),
    allowed BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_resource (resource),
    INDEX idx_allowed (allowed)
);

-- Ensure password column is large enough for bcrypt hashes
ALTER TABLE users MODIFY password VARCHAR(255) NOT NULL;

-- Add unique index on username for faster lookups
ALTER TABLE users ADD UNIQUE INDEX IF NOT EXISTS idx_unique_username (username);

-- Create backup tracking table
CREATE TABLE IF NOT EXISTS backup_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_file VARCHAR(255),
    backup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    backup_size BIGINT,
    success BOOLEAN,
    error_message TEXT,
    restored_from VARCHAR(255),
    INDEX idx_backup_time (backup_time)
);

-- Add default admin user (password: Admin@123 - should be changed immediately)
-- Note: This is commented out as you should add manually or create a setup script
-- INSERT INTO users (username, password, full_name, role, is_active) 
-- VALUES ('admin', 'bcrypt_hashed_password_here', 'Administrator', 'admin', 1);

COMMIT;
