# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-07

### Added - Major TDD Refactoring (Phases 3-7)

#### Phase 6: Complete CRUD Operations
- **PUT /api/projects/{id}** - Update project endpoint with partial updates
- **DELETE /api/projects/{id}** - Delete project endpoint (204 No Content)
- **GET /api/projects** - List projects with pagination (offset/limit)
- `UpdateProjectRequest` schema for flexible updates
- `update_project()` use case in domain service
- `delete_project()` use case in domain service
- `list_projects()` use case with pagination support
- `update()` method in repository port and implementation
- Paginated `find_all()` method (offset/limit parameters)
- 12 new E2E tests for CRUD operations
- Unique name fixtures using UUID for test isolation

#### Phase 7: Quality & Documentation
- GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`)
  - Automated testing on push/PR
  - Coverage reporting (Codecov integration)
  - Type checking (mypy strict)
  - Linting (ruff) and formatting (black)
  - Quality gates (80% coverage minimum)
- Comprehensive README updates
  - Testing section with all commands
  - Complete CRUD API documentation
  - Pagination examples
  - Metrics dashboard
- `REFACTORING_REPORT.md` - Complete phase-by-phase analysis
- `CONTRIBUTING.md` - Development guidelines
- `CHANGELOG.md` - This file

### Changed

#### Phase 6: CRUD Operations
- Updated `ProjectUseCasesPort` interface with new methods
- Enhanced `ProjectService` with update, delete, and list functionality
- Modified `ProjectRepositoryPort` interface with update and paginated find_all
- Updated `SQLAlchemyProjectRepository` with new implementations
- Improved router with complete CRUD endpoints
- Enhanced error handling for all new endpoints

#### Phase 7: Documentation
- Updated README.md with testing instructions and metrics
- Added "Fonctionnalités Implémentées" section to README
- Updated "Prochaines Étapes" reflecting completed work

### Security

#### Phase 5: Custom Exceptions & Error Handling (Already Implemented)
- Custom domain exceptions (`DomainError`, `DomainValidationError`, `ProjectAlreadyExistsError`, `ProjectNotFoundError`)
- Secure error handling in API router (no stack trace exposure)
- Generic 500 errors for unexpected failures
- Proper HTTP status codes (400, 404, 409, 422, 500)
- Server-side error logging

### Fixed

#### Phase 6: Bug Fixes
- Fixed mypy type errors in repository update method
- Fixed FastAPI Depends parameter ordering in list endpoint
- Fixed test isolation issues with unique name fixtures
- Resolved pagination edge cases in E2E tests

### Technical Metrics

- **Tests:** 89 passing (+39 from phase 2)
- **Coverage:** 87% (+32% from phase 2)
- **Mypy Errors:** 0 (strict mode)
- **Domain Coverage:** 100%
- **Type Safety:** 100%

---

## [1.0.0] - 2025-10-23

### Initial Release - Phases 0-5

#### Phase 0-2: Infrastructure Setup
- Complete testing infrastructure with fixtures
- Database session management with automatic cleanup
- Mock repository patterns for unit testing
- Integration test framework with in-memory SQLite
- E2E test setup with FastAPI TestClient
- 50 tests with 55% coverage

#### Phase 3: Domain Entity Tests
- 13 comprehensive entity tests
- `TestProjectValidation` suite (7 tests)
  - Empty name validation
  - Whitespace-only name validation
  - Negative budget validation
  - Zero budget validation
  - Invalid date range validation
  - Equal dates validation
- `TestProjectBusinessLogic` suite (6 tests)
  - Active status calculations
  - Days remaining calculations
  - Edge case handling
- Entity coverage: 100%

#### Phase 4: Integration & E2E Tests
- 10 repository integration tests
  - ID generation testing
  - Data persistence verification
  - Name uniqueness checks
  - CRUD operations
- 9 E2E API tests
  - Create project endpoint
  - Get project endpoint
  - API documentation endpoints (Swagger, ReDoc, OpenAPI)
  - Error handling (400, 404, 409, 422)

#### Phase 5: Custom Exceptions
- `src/domain/exceptions.py` module
  - `DomainError` base exception
  - `DomainValidationError` for business rules
  - `ProjectAlreadyExistsError` for duplicates
  - `ProjectNotFoundError` for missing resources
- 7 exception tests
- Updated service to use custom exceptions
- Secure error handling in API router

### Added - Core Features

- **FastAPI Application** - REST API with automatic documentation
- **Hexagonal Architecture** - Clean ports & adapters implementation
- **Domain Layer** - Pure Python business logic
  - `Project` entity with validation
  - `ProjectService` with business rules
  - Business methods (`is_active()`, `days_remaining()`)
- **Port Interfaces**
  - `ProjectUseCasesPort` (primary port)
  - `ProjectRepositoryPort` (secondary port)
- **Adapters**
  - FastAPI router (primary adapter)
  - SQLAlchemy repository (secondary adapter)
  - Pydantic schemas (DTOs)
- **API Endpoints**
  - `POST /api/projects` - Create project
  - `GET /api/projects/{id}` - Get project by ID
- **Database Support**
  - SQLite (default)
  - MySQL (via configuration)
  - PostgreSQL (via configuration)
- **Dependency Injection** - Simple DI container
- **API Documentation**
  - Swagger UI at `/docs`
  - ReDoc at `/redoc`
  - OpenAPI schema at `/openapi.json`

### Technical Stack

- **Python 3.13** (supports 3.10+)
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with multi-database support
- **Pydantic V2** - Data validation
- **uv** - Fast package manager
- **pytest** - Testing framework
- **mypy** - Static type checking (strict mode)
- **ruff** - Fast linting
- **black** - Code formatting
- **coverage** - Test coverage reporting

---

## Version Numbering

- **2.0.0** - Complete CRUD + CI/CD (current)
- **1.0.0** - Initial hexagonal architecture with basic CRUD (POST, GET)

---

## Links

- [GitHub Repository](https://github.com/yourusername/exemple_api_post_hexagonal)
- [Documentation](README.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Refactoring Report](documents/REFACTORING_REPORT.md)
