# Contributing to Hexagonal Architecture Project

Thank you for your interest in contributing! This document provides guidelines for developing, testing, and contributing to this project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Architecture Principles](#architecture-principles)

---

## Development Setup

### Prerequisites

- **Python 3.13+** (or 3.10+)
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **Git**

### Initial Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd exemple_api_post_hexagonal
```

2. **Install dependencies:**
```bash
# Install all dependencies including dev tools
uv sync --all-extras
```

3. **Verify installation:**
```bash
# Run tests to verify everything works
uv run pytest tests/ -v

# Check type safety
uv run mypy src/ --strict
```

### Development Workflow

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes...

# Run tests frequently
uv run pytest tests/ -v --cov=src

# Check type safety
uv run mypy src/ --strict

# Check code style
uv run ruff check src/
uv run black src/ --check

# Fix formatting issues
uv run black src/
```

---

## Project Structure

```
exemple_api_post_hexagonal/
├── src/
│   ├── domain/              # Business logic (PURE PYTHON)
│   │   ├── entities/        # Domain entities
│   │   ├── services/        # Business services
│   │   └── exceptions.py    # Domain exceptions
│   ├── ports/               # Interfaces
│   │   ├── primary/         # Input ports (use cases)
│   │   └── secondary/       # Output ports (repositories)
│   ├── adapters/            # Implementations
│   │   ├── primary/         # API layer (FastAPI)
│   │   └── secondary/       # Data layer (SQLAlchemy)
│   ├── di_container.py      # Dependency injection
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/                # Unit tests (no infrastructure)
│   ├── integration/         # Integration tests (with DB)
│   ├── e2e/                 # End-to-end tests (full API)
│   └── conftest.py          # Shared fixtures
└── documents/               # Documentation
```

---

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** on all function signatures
- **Docstrings** on all public methods (Google style)
- **Black** for formatting (line length: 88)
- **Ruff** for linting

### Type Safety

This project uses **mypy in strict mode**. All code must pass:

```bash
uv run mypy src/ --strict
```

**Type Hint Requirements:**
- All function parameters must have type hints
- All function return types must be specified
- Use `Optional[T]` for nullable values
- Use `list[T]` instead of `List[T]` (Python 3.9+)

**Example:**
```python
def create_project(
    self,
    name: str,
    budget: float,
    start_date: date,
    end_date: date
) -> Project:
    """Create a new project."""
    ...
```

### Architecture Rules

**CRITICAL:** The domain must remain pure Python:

- ❌ NO FastAPI imports in domain/
- ❌ NO SQLAlchemy imports in domain/
- ❌ NO Pydantic imports in domain/
- ✅ ONLY standard library in domain/
- ✅ Depend on PORT INTERFACES, not implementations

**Dependency Direction:**
```
Adapters → Ports → Domain
         ↓
     (all arrows point toward domain)
```

### Error Handling

- Use **custom domain exceptions** for business errors
- Never expose stack traces to API clients
- Log all errors with appropriate levels
- Return appropriate HTTP status codes

**Example:**
```python
# Domain layer
if not project:
    raise ProjectNotFoundError(project_id)

# API layer
try:
    project = use_cases.get_project(project_id)
except ProjectNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Testing Guidelines

### Test Coverage Requirements

- **Minimum:** 80% overall coverage
- **Domain:** 100% coverage (strict requirement)
- **Services:** 100% coverage
- **Repositories:** 95%+ coverage
- **API Routers:** 70%+ coverage

### Running Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific test types
uv run pytest tests/unit/ -v           # Unit tests only
uv run pytest tests/integration/ -v     # Integration tests
uv run pytest tests/e2e/ -v            # E2E tests

# With coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Coverage threshold check
uv run pytest tests/ --cov=src --cov-fail-under=80
```

### Test Structure

#### Unit Tests (tests/unit/)

**Purpose:** Test business logic in isolation

**Rules:**
- NO database access
- NO HTTP requests
- Use mock repositories
- Fast execution (<1ms per test)

**Example:**
```python
def test_create_project_success(mock_repository):
    # Arrange
    mock_repository.exists_by_name.return_value = False
    service = ProjectService(mock_repository)

    # Act
    project = service.create_project(...)

    # Assert
    assert project.name == "Test Project"
    mock_repository.save.assert_called_once()
```

#### Integration Tests (tests/integration/)

**Purpose:** Test database interactions

**Rules:**
- Use in-memory SQLite
- Use `db_session` fixture
- Test repository implementations
- Reset database between tests

**Example:**
```python
def test_save_project_persists_data(repository, db_session):
    # Arrange
    project = Project(...)

    # Act
    saved = repository.save(project)

    # Assert
    assert saved.id is not None
    db_result = db_session.query(ProjectModel).filter_by(id=saved.id).first()
    assert db_result is not None
```

#### E2E Tests (tests/e2e/)

**Purpose:** Test full API workflows

**Rules:**
- Use TestClient
- Test HTTP responses
- Use unique names (UUID) for test isolation
- Test error handling

**Example:**
```python
def test_create_project_success(client, unique_name):
    # Arrange
    payload = {
        "name": unique_name,
        "budget": 100000.0,
        ...
    }

    # Act
    response = client.post("/api/projects", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == unique_name
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>_<expected_outcome>`
- Test classes: `Test<FeatureName>`

**Examples:**
- `test_create_project_success`
- `test_create_project_rejects_duplicate_name`
- `test_update_project_not_found_returns_404`

### Fixtures

**Available fixtures (see `tests/conftest.py`):**

- `test_engine` - In-memory SQLite engine
- `db_session` - Database session with rollback
- `mock_repository` - Mock repository for unit tests
- `sample_project_data` - Valid project data dict
- `sample_project` - Project entity instance
- `unique_name` - UUID-based unique name for tests
- `client` - FastAPI TestClient (E2E tests)

---

## Pull Request Process

### Before Submitting

1. **Run all tests:**
```bash
uv run pytest tests/ -v --cov=src --cov-fail-under=80
```

2. **Type check:**
```bash
uv run mypy src/ --strict
```

3. **Lint and format:**
```bash
uv run black src/
uv run ruff check src/
```

4. **Update documentation** if needed

### PR Guidelines

1. **Branch naming:**
   - `feature/description` - New features
   - `fix/description` - Bug fixes
   - `refactor/description` - Code improvements
   - `docs/description` - Documentation

2. **Commit messages:**
   - Use conventional commits format
   - Start with verb in present tense
   - Keep first line under 72 characters

**Examples:**
```
feat: add project update endpoint
fix: resolve session leak in DI container
docs: update API documentation for CRUD operations
test: add integration tests for repository
```

3. **PR description should include:**
   - What: What does this PR do?
   - Why: Why is this change necessary?
   - How: How does it work?
   - Testing: How was it tested?
   - Breaking changes: Any breaking changes?

4. **PR checklist:**
   - [ ] Tests added/updated
   - [ ] All tests passing
   - [ ] Type checking passes (mypy strict)
   - [ ] Documentation updated
   - [ ] No merge conflicts
   - [ ] Coverage ≥ 80%

### CI/CD

The GitHub Actions CI will automatically:
- Run all tests
- Check coverage (minimum 80%)
- Verify type safety (mypy strict)
- Check linting (ruff)
- Check formatting (black)

**Your PR must pass all checks before merging.**

---

## Architecture Principles

### Hexagonal Architecture (Ports & Adapters)

**Core Principles:**

1. **Domain Independence:** The domain knows nothing about infrastructure
2. **Dependency Inversion:** All dependencies point toward the domain
3. **Port Interfaces:** Define contracts, not implementations
4. **Adapter Implementations:** Implement ports, can be swapped

### Adding New Features

#### 1. Start with the Domain

**Ask yourself:**
- Is this a business rule? → Add to entity
- Is this a use case? → Add to service
- Does it need data? → Define repository port method

**Example - Adding a new method:**
```python
# 1. Add to entity (if needed)
# src/domain/entities/project.py
class Project:
    def calculate_cost_per_day(self) -> float:
        """Business logic: cost per day."""
        duration = (self.end_date - self.start_date).days
        return self.budget / duration if duration > 0 else 0.0
```

#### 2. Define Port Interfaces

```python
# 2. Add to use cases port
# src/ports/primary/project_use_cases.py
@abstractmethod
def get_projects_by_budget_range(
    self, min_budget: float, max_budget: float
) -> list[Project]:
    pass

# 3. Add to repository port (if needed)
# src/ports/secondary/project_repository.py
@abstractmethod
def find_by_budget_range(
    self, min_budget: float, max_budget: float
) -> List[Project]:
    pass
```

#### 3. Implement in Service

```python
# 4. Implement in service
# src/domain/services/project_service.py
def get_projects_by_budget_range(
    self, min_budget: float, max_budget: float
) -> list[Project]:
    """Use case: Find projects within budget range."""
    if min_budget < 0 or max_budget < 0:
        raise DomainValidationError("Budget cannot be negative")
    if min_budget > max_budget:
        raise DomainValidationError("Min budget must be <= max budget")

    return self._repository.find_by_budget_range(min_budget, max_budget)
```

#### 4. Implement Adapters

```python
# 5. Implement in repository
# src/adapters/secondary/repositories/sqlalchemy_project_repository.py
def find_by_budget_range(
    self, min_budget: float, max_budget: float
) -> List[Project]:
    project_models = (
        self._session.query(ProjectModel)
        .filter(ProjectModel.budget >= min_budget)
        .filter(ProjectModel.budget <= max_budget)
        .all()
    )
    return [self._to_domain(pm) for pm in project_models]

# 6. Add API endpoint
# src/adapters/primary/fastapi/routers/projects_router.py
@router.get("/search")
def search_projects_by_budget(
    min_budget: float = Query(..., gt=0),
    max_budget: float = Query(..., gt=0),
    use_cases: ProjectUseCasesDep
) -> list[ProjectResponse]:
    projects = use_cases.get_projects_by_budget_range(min_budget, max_budget)
    return [ProjectResponse(...) for project in projects]
```

#### 5. Add Tests (TDD)

```python
# Unit test
def test_get_projects_by_budget_range_success(mock_repository):
    ...

# Integration test
def test_repository_find_by_budget_range(repository, db_session):
    ...

# E2E test
def test_search_projects_by_budget_api(client):
    ...
```

---

## Common Patterns

### Adding a New Entity

1. Create entity in `src/domain/entities/`
2. Add validation in `__post_init__`
3. Add business methods
4. Create tests in `tests/unit/domain/test_<entity>_entity.py`

### Adding a New Use Case

1. Add method to port interface (`src/ports/primary/`)
2. Implement in service (`src/domain/services/`)
3. Add repository method if needed
4. Add API endpoint
5. Add DTO schemas
6. Write tests (unit, integration, E2E)

### Adding Error Handling

1. Create custom exception in `src/domain/exceptions.py`
2. Raise in domain layer
3. Catch and convert in router
4. Add test for exception scenario

---

## Questions?

- Check the [README.md](README.md) for general information
- Review [REFACTORING_REPORT.md](documents/REFACTORING_REPORT.md) for architecture details
- Open an issue for questions or clarifications

---

**Happy Contributing! 🚀**
