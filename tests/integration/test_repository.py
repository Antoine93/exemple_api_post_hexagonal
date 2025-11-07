"""
Integration tests for SQLAlchemy repository.

Tests the repository implementation with a real database (SQLite in-memory).
These tests verify that the repository correctly interacts with the database.
"""
import pytest
from datetime import date, timedelta

from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
    ProjectModel,
)
from src.domain.entities.project import Project


class TestRepositorySave:
    """Test suite for repository save operations."""

    def test_save_project_generates_id(self, db_session, sample_project):
        """Test that save() generates an ID for a new project."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        assert sample_project.id is None

        # Act
        saved_project = repository.save(sample_project)

        # Assert
        assert saved_project.id is not None
        assert saved_project.id > 0

    def test_save_project_persists_data(self, db_session, sample_project):
        """Test that save() correctly persists all project data."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        saved_project = repository.save(sample_project)

        # Assert - Verify all fields are persisted correctly
        assert saved_project.name == sample_project.name
        assert saved_project.description == sample_project.description
        assert saved_project.start_date == sample_project.start_date
        assert saved_project.end_date == sample_project.end_date
        assert saved_project.budget == sample_project.budget
        assert saved_project.comment == sample_project.comment
        assert saved_project.manager_id == sample_project.manager_id

        # Verify it's actually in the database
        project_model = db_session.query(ProjectModel).filter(
            ProjectModel.id == saved_project.id
        ).first()
        assert project_model is not None
        assert project_model.name == sample_project.name


class TestRepositoryFindById:
    """Test suite for repository find_by_id operations."""

    def test_find_by_id_returns_project(self, db_session, create_project_in_db, sample_project_data):
        """Test that find_by_id() retrieves the correct project."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        project_model = create_project_in_db(sample_project_data)

        # Act
        found_project = repository.find_by_id(project_model.id)

        # Assert
        assert found_project is not None
        assert found_project.id == project_model.id
        assert found_project.name == sample_project_data["name"]
        assert found_project.description == sample_project_data["description"]
        assert found_project.budget == sample_project_data["budget"]

    def test_find_by_id_returns_none_if_not_found(self, db_session):
        """Test that find_by_id() returns None for non-existent ID."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        non_existent_id = 99999

        # Act
        found_project = repository.find_by_id(non_existent_id)

        # Assert
        assert found_project is None


class TestRepositoryExistsByName:
    """Test suite for repository exists_by_name operations."""

    def test_exists_by_name_returns_true_if_exists(self, db_session, create_project_in_db, sample_project_data):
        """Test that exists_by_name() returns True for existing project name."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        create_project_in_db(sample_project_data)

        # Act
        exists = repository.exists_by_name(sample_project_data["name"])

        # Assert
        assert exists is True

    def test_exists_by_name_returns_false_if_not_exists(self, db_session):
        """Test that exists_by_name() returns False for non-existent name."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        exists = repository.exists_by_name("Non-existent Project")

        # Assert
        assert exists is False


class TestRepositoryFindAll:
    """Test suite for repository find_all operations."""

    def test_find_all_returns_empty_list_when_no_projects(self, db_session):
        """Test that find_all() returns empty list when database is empty."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        projects = repository.find_all()

        # Assert
        assert projects == []

    def test_find_all_returns_all_projects(self, db_session, create_project_in_db):
        """Test that find_all() returns all projects from database."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        project1_data = {
            "name": "Project Alpha",
            "description": "First project",
            "start_date": today,
            "end_date": today + timedelta(days=30),
            "budget": 10000.0,
            "comment": "Comment 1",
            "manager_id": 1
        }

        project2_data = {
            "name": "Project Beta",
            "description": "Second project",
            "start_date": today,
            "end_date": today + timedelta(days=60),
            "budget": 20000.0,
            "comment": "Comment 2",
            "manager_id": 2
        }

        create_project_in_db(project1_data)
        create_project_in_db(project2_data)

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 2
        assert any(p.name == "Project Alpha" for p in projects)
        assert any(p.name == "Project Beta" for p in projects)


class TestRepositoryDelete:
    """Test suite for repository delete operations."""

    def test_delete_removes_project(self, db_session, create_project_in_db, sample_project_data):
        """Test that delete() removes project from database."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        project_model = create_project_in_db(sample_project_data)
        project_id = project_model.id

        # Verify project exists before deletion
        assert repository.find_by_id(project_id) is not None

        # Act
        result = repository.delete(project_id)

        # Assert
        assert result is True
        assert repository.find_by_id(project_id) is None

    def test_delete_returns_false_if_not_found(self, db_session):
        """Test that delete() returns False for non-existent ID."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        non_existent_id = 99999

        # Act
        result = repository.delete(non_existent_id)

        # Assert
        assert result is False
