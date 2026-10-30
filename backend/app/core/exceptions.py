"""Domain-specific exceptions for the application."""


class DomainError(Exception):
    """Base exception for domain-specific errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Initialize the DomainError."""
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ProfileNotFoundError(DomainError):
    """Raised when a profile is not found."""

    def __init__(self, profile_id: str) -> None:
        """Initialize the ProfileNotFoundError."""
        super().__init__(f"Profile with ID '{profile_id}' not found", "PROFILE_NOT_FOUND")
        self.profile_id = profile_id


class EntityNotFoundError(DomainError):
    """Raised when a sub-entity (work experience, education, etc.) is not found within a profile."""

    def __init__(self, entity_type: str, entity_id: str, profile_id: str) -> None:
        """Initialize the EntityNotFoundError."""
        super().__init__(f"{entity_type} {entity_id} not found in profile {profile_id}", "ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.profile_id = profile_id


class MandatoryFieldsMissingError(DomainError):
    """Raised when a write leaves mandatory fields empty.

    Only a CV import may store an entry with gaps; every other write fills them.
    """

    def __init__(self, label: str, fields: list[str]) -> None:
        """Initialize the MandatoryFieldsMissingError."""
        super().__init__(f"The {label} needs {', '.join(fields)}", "MANDATORY_FIELDS_MISSING")
        self.fields = fields


class RepositoryError(DomainError):
    """Raised when repository operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        """Initialize the RepositoryError."""
        super().__init__(f"Repository operation '{operation}' failed: {reason}", "REPOSITORY_OPERATION_FAILED")
        self.operation = operation
        self.reason = reason
