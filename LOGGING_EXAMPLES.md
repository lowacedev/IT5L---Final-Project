"""
Example: Enhanced Logging with Resource Information

This shows how to log operations with proper resource tracking
"""

from app.utils.logger import SecurityAuditLogger

# Example 1: User Action with Resource
# Good: Includes what resource was affected
SecurityAuditLogger.log_user_action(
    user="admin",
    action="Create supplier",
    details="Resource: suppliers | Created supplier: ABC Electronics (ID: 5)"
)

# Example 2: Data Access with Resource
# Good: Shows what data was accessed
SecurityAuditLogger.log_data_access(
    user="admin",
    resource="staff",  # What was accessed
    access_type="READ"
)

# Example 3: Unauthorized Access with Resource
# Good: Shows what resource was denied
SecurityAuditLogger.log_unauthorized_access_attempt(
    user="cashier",
    resource="staff_management",  # What they tried to access
    action="DELETE_STAFF"
)

# Example 4: System Log (No User/Resource)
# Good: Database connections are system-level, not user-initiated
# So Username and Resource are None - this is EXPECTED
# These show infrastructure is working

# Example 5: Login (Should have Username)
# Good: Shows who logged in
SecurityAuditLogger.log_login_attempt(
    username="admin",
    success=True,
    reason="Valid password"
)

# Example 6: Password Change (Should have Username)
# Good: Shows who changed password
SecurityAuditLogger.log_password_change(
    username="cashier",
    success=True
)

"""
SUMMARY:

When Username is None:
- Database connections (DB events)
- Service initialization (SECURESERSERVICE)
- These are SYSTEM LOGS, not user-initiated

When Resource is None:
- Connection/infrastructure logs (no resource accessed)
- These are EXPECTED for system-level operations

To populate these fields, specify them in the log message:
- For Username: Always include in user-initiated actions
- For Resource: Specify what data/feature was accessed
"""
