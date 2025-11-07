"""
Domain exceptions - Custom exception classes for business errors.

These exceptions belong to the domain layer and represent business rule violations.
They provide clear, semantic error types that can be properly handled by adapters.
"""


class DomainError(Exception):
    """Base exception for all domain-related errors."""

    pass


class DomainValidationError(DomainError):
    """Exception raised when domain validation rules are violated."""

    pass


class ProjectAlreadyExistsError(DomainValidationError):
    """Exception raised when attempting to create a project with a duplicate name."""

    def __init__(self, project_name: str) -> None:
        """
        Initialize the exception.

        Args:
            project_name: The name of the project that already exists
        """
        self.project_name = project_name
        super().__init__(f"Un projet avec le nom '{project_name}' existe déjà")


class ProjectNotFoundError(DomainError):
    """Exception raised when a requested project does not exist."""

    def __init__(self, project_id: int) -> None:
        """
        Initialize the exception.

        Args:
            project_id: The ID of the project that was not found
        """
        self.project_id = project_id
        super().__init__(f"Le projet avec l'ID {project_id} n'existe pas")
