# Testing Guide

Complete guide for testing the hexagonal architecture project with pytest.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Fixtures Reference](#fixtures-reference)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)

---

## Overview

This project uses **pytest** as the testing framework with a comprehensive test suite organized by testing level:

- **Unit Tests**: Test domain logic in isolation (no infrastructure)
- **Integration Tests**: Test infrastructure components (database, repositories)
- **End-to-End Tests**: Test complete workflows through the API

### Current Test Status

```
35 tests passing (all infrastructure canary tests)
37% code coverage baseline
Ready for TDD development
```

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_setup.py                  # Canary tests (verify infrastructure)
│
├── unit/                          # Unit tests (no infrastructure)
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── test_project_entity.py      # Tests for Project entity
│   │   └── test_project_service.py     # Tests for ProjectService
│   └── adapters/
│       └── __init__.py
│
├── integration/                   # Integration tests (with database)
│   ├── __init__.py
│   └── test_repository.py              # Tests for SQLAlchemy repository
│
└── e2e/                           # End-to-end tests (full API)
    ├── __init__.py
    └── test_api.py                     # Tests for FastAPI endpoints
```

### Test Organization Principles

1. **Unit tests** (`tests/unit/`):
   - Test domain logic in isolation
   - Use mocked dependencies
   - Fast execution (no I/O)
   - No database, no HTTP calls

2. **Integration tests** (`tests/integration/`):
   - Test infrastructure components
   - Use real database (SQLite in-memory)
   - Verify data persistence
   - Test ORM mappings

3. **E2E tests** (`tests/e2e/`):
   - Test complete user workflows
   - Test through HTTP API
   - Verify full request/response cycle
   - Test validation and error handling

---

## Running Tests

### Basic Commands

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_setup.py -v

# Run specific test class
uv run pytest tests/unit/domain/test_project_entity.py::TestProjectEntity -v

# Run specific test function
uv run pytest tests/test_setup.py::test_testing_infrastructure_is_ready -v
```

### Run Tests by Category

```bash
# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Run only e2e tests
uv run pytest tests/e2e/ -v

# Run only canary tests
uv run pytest tests/test_setup.py -v
```

### Advanced Options

```bash
# Stop on first failure
uv run pytest tests/ -x

# Run last failed tests only
uv run pytest tests/ --lf

# Run tests matching a pattern
uv run pytest tests/ -k "entity"

# Show print statements
uv run pytest tests/ -s

# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
# Opens htmlcov/index.html in browser
```

### Watch Mode (for TDD)

```bash
# Install pytest-watch (optional)
uv add --dev pytest-watch

# Run tests automatically on file changes
uv run ptw tests/ -- -v
```

---

## Fixtures Reference

Fixtures are defined in `tests/conftest.py` and are automatically available to all tests.

### Database Fixtures

#### `test_engine`

Creates an in-memory SQLite engine for testing.

```python
def test_example(test_engine):
    # test_engine is a SQLAlchemy engine
    # Tables are created automatically
    # Cleaned up after test
    pass
```

**Scope**: `function` (fresh database for each test)

#### `db_session`

Provides a database session with automatic rollback.

```python
def test_example(db_session):
    # db_session is a SQLAlchemy Session
    # Changes are rolled back after test
    # Ensures test isolation
    pass
```

**Scope**: `function` (isolated for each test)

**Features**:
- Automatic rollback (changes don't persist)
- Fresh session for each test
- Connection automatically closed

### Mock Fixtures

#### `mock_repository`

Mock implementation of `ProjectRepositoryPort` for unit testing.

```python
def test_example(mock_repository):
    # Configure mock behavior
    mock_repository.exists_by_name.return_value = False
    mock_repository.save.return_value = some_project

    # Use in service
    service = ProjectService(mock_repository)

    # Verify interactions
    mock_repository.save.assert_called_once()
```

**Use cases**:
- Testing domain services without database
- Verifying method calls
- Controlling return values

### Test Data Fixtures

#### `sample_project_data`

Dictionary with valid project data.

```python
def test_example(sample_project_data):
    # sample_project_data is a dict with:
    # - name: "Test Project"
    # - description: "A test project description"
    # - start_date: today
    # - end_date: today + 365 days
    # - budget: 100000.0
    # - comment: "This is a test comment"
    # - manager_id: 1
    pass
```

#### `sample_project`

Project entity without ID (not yet saved).

```python
def test_example(sample_project):
    # sample_project is a Project entity
    assert sample_project.id is None
    assert sample_project.name == "Test Project"
```

#### `sample_project_with_id`

Project entity with ID=1 (simulates saved project).

```python
def test_example(sample_project_with_id):
    # sample_project_with_id has id=1
    assert sample_project_with_id.id == 1
```

#### `multiple_projects`

List of three different Project entities.

```python
def test_example(multiple_projects):
    # multiple_projects is a list of 3 projects
    assert len(multiple_projects) == 3
    assert multiple_projects[0].name == "Project Alpha"
```

### Helper Fixtures

#### `create_project_in_db`

Factory function to create projects directly in the test database.

```python
def test_example(db_session, create_project_in_db, sample_project_data):
    # Create a project in the database
    project_model = create_project_in_db(sample_project_data)

    # project_model is a ProjectModel (ORM) with id
    assert project_model.id is not None

    # Can be queried from db_session
    result = db_session.query(ProjectModel).filter_by(id=project_model.id).first()
    assert result is not None
```

---

## Writing Tests

### Unit Test Example (Domain Entity)

```python
# tests/unit/domain/test_project_entity.py
import pytest
from datetime import date, timedelta
from src.domain.entities.project import Project

class TestProjectValidation:
    """Test entity validation rules."""

    def test_create_valid_project(self, sample_project_data):
        """Test that a valid project can be created."""
        project = Project(id=None, **sample_project_data)

        assert project.name == "Test Project"
        assert project.budget == 100000.0

    def test_empty_name_raises_error(self, sample_project_data):
        """Test that empty name raises ValueError."""
        sample_project_data["name"] = ""

        with pytest.raises(ValueError, match="nom du projet ne peut pas être vide"):
            Project(id=None, **sample_project_data)

    def test_negative_budget_raises_error(self, sample_project_data):
        """Test that negative budget raises ValueError."""
        sample_project_data["budget"] = -1000.0

        with pytest.raises(ValueError, match="budget doit être positif"):
            Project(id=None, **sample_project_data)
```

### Unit Test Example (Domain Service)

```python
# tests/unit/domain/test_project_service.py
import pytest
from datetime import date, timedelta
from src.domain.services.project_service import ProjectService

class TestProjectServiceCreate:
    """Test ProjectService.create_project()."""

    def test_create_project_success(self, mock_repository, sample_project_with_id):
        """Test successful project creation."""
        # Arrange: Configure mock
        mock_repository.exists_by_name.return_value = False
        mock_repository.save.return_value = sample_project_with_id

        service = ProjectService(mock_repository)

        # Act: Create project
        result = service.create_project(
            name="Test Project",
            description="Description",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            budget=100000.0,
            comment="Comment",
            manager_id=1,
        )

        # Assert: Verify result and interactions
        assert result.id == 1
        assert result.name == "Test Project"
        mock_repository.exists_by_name.assert_called_once_with("Test Project")
        mock_repository.save.assert_called_once()

    def test_create_project_duplicate_name(self, mock_repository):
        """Test that duplicate name raises ValueError."""
        # Arrange: Name already exists
        mock_repository.exists_by_name.return_value = True

        service = ProjectService(mock_repository)

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError, match="existe déjà"):
            service.create_project(
                name="Existing Project",
                description="Description",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                budget=100000.0,
                comment="Comment",
                manager_id=1,
            )

        # Verify save was NOT called
        mock_repository.save.assert_not_called()
```

### Integration Test Example (Repository)

```python
# tests/integration/test_repository.py
import pytest
from datetime import date, timedelta
from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from src.domain.entities.project import Project

class TestRepositorySave:
    """Test repository save operations."""

    def test_save_creates_project_with_id(self, db_session, sample_project):
        """Test that save() persists project and generates ID."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        saved_project = repository.save(sample_project)

        # Assert
        assert saved_project.id is not None
        assert saved_project.name == sample_project.name

        # Verify in database
        found_project = repository.find_by_id(saved_project.id)
        assert found_project is not None
        assert found_project.name == sample_project.name
```

### E2E Test Example (API)

```python
# tests/e2e/test_api.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_project_success():
    """Test POST /api/projects returns 201 Created."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Arrange
        project_data = {
            "name": "API Test Project",
            "description": "Testing API",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "budget": 100000.0,
            "comment": "Test comment",
            "manager_id": 1,
        }

        # Act
        response = await client.post("/api/projects", json=project_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "API Test Project"
        assert data["is_active"] is True
```

---

## Test Coverage

### View Coverage Reports

```bash
# Terminal report with missing lines
uv run pytest tests/ --cov=src --cov-report=term-missing

# HTML report (opens in browser)
uv run pytest tests/ --cov=src --cov-report=html
```

### Coverage Goals by Phase

- **Phase 0** (Infrastructure): 37% baseline
- **Phase 1** (Unit tests): 80%+ domain coverage
- **Phase 2** (Integration): 90%+ overall coverage
- **Phase 3** (E2E): 95%+ overall coverage

### Exclude from Coverage

Already configured in `pyproject.toml`:

```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## Best Practices

### 1. Test Naming Convention

```python
# Use descriptive names that explain what is tested
def test_create_project_with_valid_data_succeeds():
    pass

def test_create_project_with_empty_name_raises_value_error():
    pass

def test_create_project_with_duplicate_name_raises_value_error():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange: Setup test data and mocks
    mock_repo.exists_by_name.return_value = False
    service = ProjectService(mock_repo)

    # Act: Execute the code under test
    result = service.create_project(...)

    # Assert: Verify the result
    assert result.id is not None
    mock_repo.save.assert_called_once()
```

### 3. One Assertion Per Test (when possible)

```python
# Good: Tests one specific behavior
def test_empty_name_raises_value_error():
    with pytest.raises(ValueError, match="nom du projet"):
        Project(id=None, name="", ...)

# Good: Tests another specific behavior
def test_negative_budget_raises_value_error():
    with pytest.raises(ValueError, match="budget doit être positif"):
        Project(id=None, budget=-100, ...)
```

### 4. Use Fixtures for Test Data

```python
# Good: Use fixtures
def test_example(sample_project, mock_repository):
    service = ProjectService(mock_repository)
    # ...

# Bad: Create data in every test
def test_example():
    project = Project(id=1, name="Test", description="Test", ...)
    # ... repeated in every test
```

### 5. Test Edge Cases

```python
def test_project_with_zero_budget_raises_error():
    """Budget must be strictly positive (> 0)."""
    pass

def test_project_with_same_start_and_end_date_raises_error():
    """End date must be AFTER start date."""
    pass

def test_days_remaining_for_past_project_returns_zero():
    """Past projects should have 0 days remaining."""
    pass
```

### 6. Use Parametrize for Multiple Cases

```python
@pytest.mark.parametrize("budget,should_fail", [
    (-1000, True),   # Negative
    (0, True),       # Zero
    (0.01, False),   # Positive
    (100000, False), # Normal
])
def test_budget_validation(budget, should_fail):
    if should_fail:
        with pytest.raises(ValueError):
            Project(id=None, budget=budget, ...)
    else:
        project = Project(id=None, budget=budget, ...)
        assert project.budget == budget
```

### 7. Mock External Dependencies

```python
# Good: Mock repository in unit tests
def test_service_logic(mock_repository):
    service = ProjectService(mock_repository)
    # Test service logic without database

# Good: Use real database in integration tests
def test_repository_persistence(db_session):
    repository = SQLAlchemyProjectRepository(db_session)
    # Test actual database operations
```

### 8. Test Error Messages

```python
def test_empty_name_has_clear_error_message():
    """Error messages should be clear and helpful."""
    with pytest.raises(ValueError) as exc_info:
        Project(id=None, name="", ...)

    assert "nom du projet ne peut pas être vide" in str(exc_info.value)
```

### 9. Keep Tests Independent

```python
# Good: Each test is independent
def test_create_project(db_session):
    repository = SQLAlchemyProjectRepository(db_session)
    # ... test creates its own data

def test_find_project(db_session, create_project_in_db):
    # ... test creates its own data
    project = create_project_in_db(...)
    repository = SQLAlchemyProjectRepository(db_session)
    # ... test logic

# Bad: Tests depend on execution order
def test_create_project():
    global created_project_id
    # ... saves ID for next test

def test_find_project():
    # ... uses created_project_id from previous test
```

### 10. Document Test Intent

```python
def test_create_project_checks_name_uniqueness(mock_repository):
    """
    Business rule: Project names must be unique.

    The service should check if a project with the same name
    exists before creating a new one.
    """
    mock_repository.exists_by_name.return_value = True

    service = ProjectService(mock_repository)

    with pytest.raises(ValueError, match="existe déjà"):
        service.create_project(name="Existing", ...)
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Solution**: pytest uses `pythonpath` from `pyproject.toml`. Ensure you're running from the project root:

```bash
cd C:\Users\Antoine\Desktop\exemple_api_post_hexagonal
uv run pytest tests/
```

#### 2. Database Lock Errors

```
sqlite3.OperationalError: database is locked
```

**Solution**: Use `db_session` fixture instead of creating your own session. The fixture handles transactions properly.

#### 3. Test Isolation Issues

**Problem**: Tests pass individually but fail when run together.

**Solution**:
- Always use `db_session` fixture (auto-rollback)
- Don't share mutable state between tests
- Don't rely on test execution order

#### 4. SQLAlchemy 2.0 Warnings

```
MovedIn20Warning: The declarative_base() function is now available as...
```

**Solution**: This is a deprecation warning in the source code. Will be fixed in Phase 2.

For test code, use:
```python
from sqlalchemy import text

# Use text() for raw SQL
db_session.execute(text("SELECT 1"))
```

---

## Next Steps

### Phase 1: Unit Tests (Domain Layer)

Write comprehensive unit tests for:
- `tests/unit/domain/test_project_entity.py`
- `tests/unit/domain/test_project_service.py`

**Goal**: 80%+ coverage of domain layer

### Phase 2: Integration Tests

Write integration tests for:
- `tests/integration/test_repository.py`

**Goal**: 90%+ coverage including repository

### Phase 3: E2E Tests

Write end-to-end tests for:
- `tests/e2e/test_api.py`

**Goal**: 95%+ overall coverage

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Pytest Fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **Coverage.py**: https://coverage.readthedocs.io/
- **TDD with Python**: https://www.obeythetestinggoat.com/

---

**Testing Infrastructure Status**: READY FOR TDD

All 35 canary tests passing. You can now proceed with Phase 1 (Unit Tests).
