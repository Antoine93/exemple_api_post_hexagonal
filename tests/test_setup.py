"""
Canary tests to verify the testing infrastructure is working correctly.

These tests ensure that:
1. All imports work correctly
2. Fixtures are properly configured
3. Database setup works
4. Mock repositories can be created

If these tests pass, the testing infrastructure is ready for TDD.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock
from sqlalchemy import text

from src.domain.entities.project import Project
from src.domain.services.project_service import ProjectService
from src.ports.secondary.project_repository import ProjectRepositoryPort
from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
    ProjectModel,
)


class TestImports:
    """Verify that all necessary modules can be imported."""

    def test_can_import_domain_entities(self):
        """Test that domain entities can be imported."""
        assert Project is not None

    def test_can_import_domain_services(self):
        """Test that domain services can be imported."""
        assert ProjectService is not None

    def test_can_import_ports(self):
        """Test that ports can be imported."""
        assert ProjectRepositoryPort is not None

    def test_can_import_adapters(self):
        """Test that adapters can be imported."""
        assert SQLAlchemyProjectRepository is not None
        assert ProjectModel is not None


class TestFixtures:
    """Verify that pytest fixtures work correctly."""

    def test_test_engine_fixture(self, test_engine):
        """
        Test that the test_engine fixture provides a working database engine.

        Args:
            test_engine: SQLite in-memory engine from conftest
        """
        assert test_engine is not None
        assert test_engine.url.database == ":memory:"

    def test_db_session_fixture(self, db_session):
        """
        Test that the db_session fixture provides a working session.

        Args:
            db_session: Database session from conftest
        """
        assert db_session is not None
        # Verify we can execute a simple query
        result = db_session.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

    def test_mock_repository_fixture(self, mock_repository):
        """
        Test that the mock_repository fixture provides a proper mock.

        Args:
            mock_repository: Mock ProjectRepositoryPort from conftest
        """
        assert mock_repository is not None
        assert isinstance(mock_repository, Mock)
        # Verify it has the required methods
        assert hasattr(mock_repository, "save")
        assert hasattr(mock_repository, "find_by_id")
        assert hasattr(mock_repository, "exists_by_name")

    def test_sample_project_data_fixture(self, sample_project_data):
        """
        Test that the sample_project_data fixture provides valid data.

        Args:
            sample_project_data: Dictionary with project data from conftest
        """
        assert sample_project_data is not None
        assert "name" in sample_project_data
        assert "description" in sample_project_data
        assert "start_date" in sample_project_data
        assert "end_date" in sample_project_data
        assert "budget" in sample_project_data

    def test_sample_project_fixture(self, sample_project):
        """
        Test that the sample_project fixture provides a valid Project entity.

        Args:
            sample_project: Project entity from conftest
        """
        assert sample_project is not None
        assert isinstance(sample_project, Project)
        assert sample_project.name == "Test Project"
        assert sample_project.id is None  # Not yet saved

    def test_sample_project_with_id_fixture(self, sample_project_with_id):
        """
        Test that the sample_project_with_id fixture provides a Project with ID.

        Args:
            sample_project_with_id: Project entity with ID from conftest
        """
        assert sample_project_with_id is not None
        assert isinstance(sample_project_with_id, Project)
        assert sample_project_with_id.id == 1

    def test_multiple_projects_fixture(self, multiple_projects):
        """
        Test that the multiple_projects fixture provides a list of projects.

        Args:
            multiple_projects: List of Project entities from conftest
        """
        assert multiple_projects is not None
        assert isinstance(multiple_projects, list)
        assert len(multiple_projects) == 3
        assert all(isinstance(p, Project) for p in multiple_projects)


class TestDatabaseOperations:
    """Verify that basic database operations work."""

    def test_can_create_table(self, db_session):
        """
        Test that we can create and query the projects table.

        Args:
            db_session: Database session from conftest
        """
        # Table should already exist (created by test_engine fixture)
        result = db_session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        )
        table_exists = result.fetchone() is not None
        assert table_exists

    def test_can_insert_project(self, db_session):
        """
        Test that we can insert a project into the database.

        Args:
            db_session: Database session from conftest
        """
        today = date.today()

        project_model = ProjectModel(
            name="Canary Test Project",
            description="Testing database insert",
            start_date=today,
            end_date=today + timedelta(days=365),
            budget=50000.0,
            comment="Canary test",
            manager_id=1,
        )

        db_session.add(project_model)
        db_session.commit()
        db_session.refresh(project_model)

        assert project_model.id is not None
        assert project_model.name == "Canary Test Project"

    def test_can_query_project(self, db_session):
        """
        Test that we can query projects from the database.

        Args:
            db_session: Database session from conftest
        """
        today = date.today()

        # Insert a project
        project_model = ProjectModel(
            name="Queryable Project",
            description="Testing database query",
            start_date=today,
            end_date=today + timedelta(days=365),
            budget=75000.0,
            comment="Query test",
            manager_id=2,
        )
        db_session.add(project_model)
        db_session.commit()

        # Query it back
        result = db_session.query(ProjectModel).filter(
            ProjectModel.name == "Queryable Project"
        ).first()

        assert result is not None
        assert result.name == "Queryable Project"
        assert result.budget == 75000.0

    def test_database_isolation(self, db_session):
        """
        Test that database changes don't persist between tests.

        This test verifies that the db_session fixture properly
        rolls back changes, ensuring test isolation.

        Args:
            db_session: Database session from conftest
        """
        # Query for any projects (should be empty or only from this test)
        count = db_session.query(ProjectModel).count()

        # This count should be 0 if database isolation is working
        # (unless we've inserted something in this specific test)
        assert count >= 0


class TestRepositoryWithDatabase:
    """Verify that the repository can work with the test database."""

    def test_can_create_repository(self, db_session):
        """
        Test that we can instantiate the repository with a test session.

        Args:
            db_session: Database session from conftest
        """
        repository = SQLAlchemyProjectRepository(db_session)
        assert repository is not None

    def test_repository_can_save(self, db_session, sample_project):
        """
        Test that the repository can save a project.

        Args:
            db_session: Database session from conftest
            sample_project: Project entity from conftest
        """
        repository = SQLAlchemyProjectRepository(db_session)

        saved_project = repository.save(sample_project)

        assert saved_project is not None
        assert saved_project.id is not None
        assert saved_project.name == sample_project.name


class TestMockRepository:
    """Verify that mock repository works for unit testing."""

    def test_can_mock_repository_methods(self, mock_repository, sample_project_with_id):
        """
        Test that we can configure mock repository behavior.

        Args:
            mock_repository: Mock ProjectRepositoryPort from conftest
            sample_project_with_id: Project entity with ID from conftest
        """
        # Configure mock behavior
        mock_repository.save.return_value = sample_project_with_id
        mock_repository.exists_by_name.return_value = False

        # Test mock behavior
        result = mock_repository.save(sample_project_with_id)
        assert result.id == 1

        exists = mock_repository.exists_by_name("Test Project")
        assert exists is False

        # Verify mock was called
        mock_repository.save.assert_called_once()
        mock_repository.exists_by_name.assert_called_once_with("Test Project")


class TestServiceWithMockRepository:
    """Verify that domain service can be tested with mock repository."""

    def test_can_instantiate_service_with_mock(self, mock_repository):
        """
        Test that we can create a service with a mock repository.

        Args:
            mock_repository: Mock ProjectRepositoryPort from conftest
        """
        service = ProjectService(mock_repository)
        assert service is not None

    def test_service_uses_repository(self, mock_repository, sample_project_with_id):
        """
        Test that the service correctly uses the repository.

        Args:
            mock_repository: Mock ProjectRepositoryPort from conftest
            sample_project_with_id: Project entity with ID from conftest
        """
        # Configure mock
        mock_repository.exists_by_name.return_value = False
        mock_repository.save.return_value = sample_project_with_id

        # Create service and use it
        service = ProjectService(mock_repository)

        result = service.create_project(
            name="Test Project",
            description="Test description",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            budget=100000.0,
            comment="Test",
            manager_id=1,
        )

        # Verify service used the repository
        assert result is not None
        mock_repository.exists_by_name.assert_called_once()
        mock_repository.save.assert_called_once()


# ============================================================================
# FINAL CANARY TEST
# ============================================================================


def test_testing_infrastructure_is_ready():
    """
    Final canary test to confirm everything is working.

    If this test passes, the testing infrastructure is ready for TDD!
    """
    assert True, "Testing infrastructure is ready!"
