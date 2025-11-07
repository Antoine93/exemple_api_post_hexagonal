"""
Unit tests for domain exceptions.

Tests the custom exception classes to ensure they provide proper error messages.
"""
import pytest

from src.domain.exceptions import (
    DomainError,
    DomainValidationError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)


class TestDomainExceptionHierarchy:
    """Test suite for exception inheritance hierarchy."""

    def test_domain_validation_error_inherits_from_domain_error(self):
        """Test that DomainValidationError is a subclass of DomainError."""
        assert issubclass(DomainValidationError, DomainError)

    def test_project_already_exists_error_inherits_from_validation_error(self):
        """Test that ProjectAlreadyExistsError is a subclass of DomainValidationError."""
        assert issubclass(ProjectAlreadyExistsError, DomainValidationError)

    def test_project_not_found_error_inherits_from_domain_error(self):
        """Test that ProjectNotFoundError is a subclass of DomainError."""
        assert issubclass(ProjectNotFoundError, DomainError)


class TestProjectAlreadyExistsError:
    """Test suite for ProjectAlreadyExistsError."""

    def test_exception_message_includes_project_name(self):
        """Test that exception message includes the project name."""
        # Arrange
        project_name = "Duplicate Project"

        # Act
        exception = ProjectAlreadyExistsError(project_name)

        # Assert
        assert str(exception) == "Un projet avec le nom 'Duplicate Project' existe déjà"
        assert exception.project_name == project_name

    def test_exception_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        # Arrange
        project_name = "Test Project"

        # Act & Assert
        with pytest.raises(ProjectAlreadyExistsError) as exc_info:
            raise ProjectAlreadyExistsError(project_name)

        assert exc_info.value.project_name == project_name


class TestProjectNotFoundError:
    """Test suite for ProjectNotFoundError."""

    def test_exception_message_includes_project_id(self):
        """Test that exception message includes the project ID."""
        # Arrange
        project_id = 42

        # Act
        exception = ProjectNotFoundError(project_id)

        # Assert
        assert str(exception) == "Le projet avec l'ID 42 n'existe pas"
        assert exception.project_id == project_id

    def test_exception_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        # Arrange
        project_id = 999

        # Act & Assert
        with pytest.raises(ProjectNotFoundError) as exc_info:
            raise ProjectNotFoundError(project_id)

        assert exc_info.value.project_id == project_id
