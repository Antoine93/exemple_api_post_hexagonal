"""
Unit tests for ProjectService.

Tests the domain service business logic with mocked repositories.
No real database - testing domain logic in isolation.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from src.domain.services.project_service import ProjectService
from src.domain.entities.project import Project
from src.domain.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from src.ports.primary.project_use_cases import ProjectUseCasesPort


class TestProjectServiceArchitecture:
    """Test suite for architectural compliance."""

    def test_project_service_implements_use_cases_port(self):
        """Service MUST implement ProjectUseCasesPort interface."""
        assert issubclass(ProjectService, ProjectUseCasesPort), \
            "ProjectService must inherit from ProjectUseCasesPort"

    def test_project_service_has_all_interface_methods(self, mock_repository):
        """Service must have all methods defined in the interface."""
        service = ProjectService(mock_repository)

        # Check all abstract methods are implemented
        required_methods = ['create_project', 'get_project']
        for method_name in required_methods:
            assert hasattr(service, method_name), \
                f"ProjectService must have method {method_name}"
            assert callable(getattr(service, method_name)), \
                f"ProjectService.{method_name} must be callable"


class TestCreateProject:
    """Tests du cas d'usage create_project."""

    def test_create_project_success(self, mock_repository, sample_project_data):
        """Créer un projet avec succès."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_name.return_value = False

        expected_project = Project(id=1, **sample_project_data)
        mock_repository.save.return_value = expected_project

        # Act
        result = service.create_project(**sample_project_data)

        # Assert
        mock_repository.exists_by_name.assert_called_once_with(sample_project_data["name"])
        mock_repository.save.assert_called_once()
        assert result.id == 1
        assert result.name == sample_project_data["name"]

    def test_create_project_rejects_duplicate_name(self, mock_repository, sample_project_data):
        """Ne pas créer un projet avec un nom existant."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_name.return_value = True

        # Act & Assert
        with pytest.raises(ProjectAlreadyExistsError) as exc_info:
            service.create_project(**sample_project_data)

        assert exc_info.value.project_name == sample_project_data["name"]
        # Verify save was never called
        mock_repository.save.assert_not_called()

    def test_create_project_validates_entity_rules(self, mock_repository):
        """Les règles de l'entité doivent être validées."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_name.return_value = False

        today = date.today()
        invalid_data = {
            "name": "Test Project",
            "description": "Test",
            "start_date": today,
            "end_date": today - timedelta(days=1),  # End before start - INVALID
            "budget": 100000.0,
            "comment": "Test",
            "manager_id": 1
        }

        # Act & Assert
        with pytest.raises(ValueError, match="date de fin doit être après"):
            service.create_project(**invalid_data)

        # Verify save was never called
        mock_repository.save.assert_not_called()

    def test_create_project_validates_positive_budget(self, mock_repository):
        """Le budget doit être positif."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_name.return_value = False

        today = date.today()
        invalid_data = {
            "name": "Test Project",
            "description": "Test",
            "start_date": today,
            "end_date": today + timedelta(days=365),
            "budget": -1000.0,  # Negative budget - INVALID
            "comment": "Test",
            "manager_id": 1
        }

        # Act & Assert
        with pytest.raises(ValueError, match="budget doit être positif"):
            service.create_project(**invalid_data)


class TestGetProject:
    """Tests du cas d'usage get_project."""

    def test_get_project_success(self, mock_repository, sample_project_with_id):
        """Récupérer un projet existant."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id

        # Act
        result = service.get_project(1)

        # Assert
        mock_repository.find_by_id.assert_called_once_with(1)
        assert result.id == 1
        assert result.name == sample_project_with_id.name

    def test_get_project_not_found(self, mock_repository):
        """Erreur si projet n'existe pas."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError) as exc_info:
            service.get_project(999)

        assert exc_info.value.project_id == 999
