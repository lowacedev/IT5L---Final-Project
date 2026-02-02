


class ValidationError(Exception):
    """Raised when business rule validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass


class DuplicateError(Exception):
    """Raised when trying to create a duplicate resource."""
    pass


class PermissionError(Exception):
    """Raised when user doesn't have permission for an action."""
    pass


class DatabaseError(Exception):
    """Raised when database operation fails."""
    pass
