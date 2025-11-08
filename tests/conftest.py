"""
Pytest configuration and fixtures for the hexagonal architecture project.

This file contains reusable fixtures for:
- Database testing (in-memory SQLite)
- Mock repositories
- Test data factories
- E2E testing with isolated databases
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType
from src.ports.secondary.project_repository import ProjectRepositoryPort
from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    ProjectModel,
    Base,
)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def test_engine():
    """
    Create an in-memory SQLite engine for testing.

    Scope: function - Creates a fresh database for each test.
    This ensures complete test isolation.

    Returns:
        SQLAlchemy Engine configured with SQLite in-memory database
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup: Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Create a database session with automatic rollback.

    This fixture:
    1. Creates a new session for each test
    2. Automatically rolls back changes after the test
    3. Ensures test isolation

    Args:
        test_engine: The in-memory SQLite engine

    Returns:
        SQLAlchemy Session that will be automatically rolled back
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    # Cleanup: Rollback transaction and close connections
    session.close()
    transaction.rollback()
    connection.close()


# ============================================================================
# MOCK FIXTURES
# ============================================================================


@pytest.fixture
def mock_repository():
    """
    Create a mock ProjectRepositoryPort for unit testing.

    This fixture is useful for testing domain services in isolation
    without needing a real database.

    Returns:
        Mock object implementing ProjectRepositoryPort interface
    """
    mock = Mock(spec=ProjectRepositoryPort)
    return mock


# ============================================================================
# TEST DATA FACTORIES
# ============================================================================


@pytest.fixture
def sample_project_data():
    """
    Provide sample project data for tests.

    Returns:
        dict: Valid project data that can be used to create Project entities
    """
    today = date.today()
    return {
        "numero": "PROJ-001",
        "nom": "Test Project",
        "description": "A test project description",
        "date_debut": today,
        "date_echeance": today + timedelta(days=365),
        "type": ProjectType.INTERNAL,
        "stade": "En cours",
        "commentaire": "This is a test comment",
        "heures_planifiees": 100.0,
        "heures_reelles": 0.0,
        "est_template": False,
        "projet_template_id": None,
        "responsable_id": 1,
        "entreprise_id": 1,
        "contact_id": None,
    }


@pytest.fixture
def sample_project(sample_project_data):
    """
    Create a sample Project entity for tests.

    Args:
        sample_project_data: Dictionary with project data

    Returns:
        Project: A valid Project entity with id=None
    """
    from datetime import datetime
    return Project(
        id=None,
        date_creation=datetime.now(),
        **sample_project_data
    )


@pytest.fixture
def sample_project_with_id(sample_project_data):
    """
    Create a sample Project entity with an ID (simulating a saved project).

    Args:
        sample_project_data: Dictionary with project data

    Returns:
        Project: A valid Project entity with id=1
    """
    from datetime import datetime
    return Project(
        id=1,
        date_creation=datetime.now(),
        **sample_project_data
    )


@pytest.fixture
def multiple_projects():
    """
    Create multiple project entities for testing list operations.

    Returns:
        list[Project]: List of three different Project entities
    """
    from datetime import datetime
    today = date.today()

    projects = [
        Project(
            id=1,
            numero="PROJ-ALPHA",
            nom="Project Alpha",
            description="First test project",
            date_debut=today,
            date_echeance=today + timedelta(days=365),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire="Alpha comment",
            heures_planifiees=100.0,
            heures_reelles=20.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now(),
        ),
        Project(
            id=2,
            numero="PROJ-BETA",
            nom="Project Beta",
            description="Second test project",
            date_debut=today + timedelta(days=30),
            date_echeance=today + timedelta(days=395),
            type=ProjectType.EXTERNAL,
            stade="Planifié",
            commentaire="Beta comment",
            heures_planifiees=200.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=2,
            entreprise_id=2,
            contact_id=1,
            date_creation=datetime.now(),
        ),
        Project(
            id=3,
            numero="PROJ-GAMMA",
            nom="Project Gamma",
            description="Third test project",
            date_debut=today - timedelta(days=30),
            date_echeance=today + timedelta(days=335),
            type=ProjectType.MAINTENANCE,
            stade="Terminé",
            commentaire="Gamma comment",
            heures_planifiees=150.0,
            heures_reelles=180.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now(),
        ),
    ]

    return projects


# ============================================================================
# HELPER FIXTURES
# ============================================================================


@pytest.fixture
def create_project_in_db(db_session):
    """
    Factory fixture to create projects directly in the test database.

    This is useful for integration tests where you need to pre-populate
    the database with test data.

    Args:
        db_session: The test database session

    Returns:
        Callable that creates a ProjectModel in the database
    """
    def _create_project(project_data: dict) -> ProjectModel:
        """
        Create a project in the database.

        Args:
            project_data: Dictionary with project fields

        Returns:
            ProjectModel: The created project model
        """
        from datetime import datetime
        # Add date_creation if not provided
        if "date_creation" not in project_data:
            project_data = {**project_data, "date_creation": datetime.now()}

        # Convert ProjectType enum to string if necessary
        if "type" in project_data and isinstance(project_data["type"], ProjectType):
            project_data = {**project_data, "type": project_data["type"].value}

        project_model = ProjectModel(**project_data)
        db_session.add(project_model)
        db_session.commit()
        db_session.refresh(project_model)
        return project_model

    return _create_project


# ============================================================================
# E2E TESTING FIXTURES (Isolated Database)
# ============================================================================


@pytest.fixture(scope="function")
def isolated_db_engine():
    """
    Create an isolated in-memory database engine for E2E tests.

    This ensures complete isolation between E2E tests by creating
    a fresh database for each test function.

    Scope: function - New database per test for complete isolation

    Returns:
        SQLAlchemy Engine with isolated in-memory database
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables in the isolated database
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def isolated_db_session(isolated_db_engine) -> Generator[Session, None, None]:
    """
    Create an isolated database session for E2E tests.

    This session is connected to an isolated in-memory database,
    ensuring no cross-contamination between tests.

    Args:
        isolated_db_engine: The isolated database engine

    Yields:
        SQLAlchemy Session connected to isolated database
    """
    connection = isolated_db_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(isolated_db_session) -> TestClient:
    """
    Create a FastAPI TestClient with isolated database for E2E tests.

    This fixture:
    1. Creates a fresh isolated database for the test
    2. Patches the DI container to use the isolated DB
    3. Provides a TestClient for making HTTP requests
    4. Automatically cleans up after the test

    IMPORTANT: This fixture ensures E2E tests are completely isolated
    from each other and don't share database state.

    Args:
        isolated_db_session: The isolated database session

    Returns:
        TestClient: FastAPI test client with isolated database

    Example:
        def test_create_project(client):
            response = client.post("/api/projects", json={...})
            assert response.status_code == 201
    """
    from unittest.mock import patch
    from src.main import app

    # We need to patch the get_db_session function in di_container
    # to return our isolated session instead of creating a new one
    def override_get_db_session() -> Generator[Session, None, None]:
        """Override function that returns the isolated test session."""
        try:
            yield isolated_db_session
        finally:
            pass  # Cleanup is handled by the isolated_db_session fixture

    # Patch the DI container's get_db_session function
    with patch('src.di_container.get_db_session', override_get_db_session):
        # Create the test client with the patched dependency
        test_client = TestClient(app)

        yield test_client


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """
    Configure pytest with custom markers.

    This allows categorizing tests:
    - unit: Unit tests (fast, no external dependencies)
    - integration: Integration tests (with database)
    - e2e: End-to-end tests (full API tests)
    - flaky: Tests that are known to be flaky
    - slow: Tests that take longer to run
    """
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (with database)"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests (full stack)"
    )
    config.addinivalue_line(
        "markers", "flaky: marks tests as flaky (may fail intermittently)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (take more than 1 second)"
    )
