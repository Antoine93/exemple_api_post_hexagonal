# Plan de Mise à Jour TDD - Projet Architecture Hexagonale

**Date:** 2025-11-06
**Méthodologie:** Test-Driven Development (TDD)
**Objectif:** Corriger les bugs critiques et améliorer le projet via une approche TDD

---

## Philosophie TDD

```
RED → GREEN → REFACTOR
  ↓      ↓        ↓
Écrire  Faire   Améliorer
le test passer  le code
(échec) le test (qualité)
```

**Règle d'or:** Ne jamais écrire de code de production sans avoir d'abord écrit un test qui échoue.

---

## Vue d'Ensemble des Phases

| Phase | Durée | Agent Spécialisé | Objectif Principal |
|-------|-------|------------------|-------------------|
| **Phase 0** | 2h | **Setup Agent** | Infrastructure de tests |
| **Phase 1** | 1 jour | **Critical Fix Agent** | Bugs bloquants (sessions, encoding) |
| **Phase 2** | 2 jours | **Architecture Agent** | Conformité hexagonale |
| **Phase 3** | 2 jours | **Domain Agent** | Tests domaine métier |
| **Phase 4** | 2 jours | **Integration Agent** | Tests adapters |
| **Phase 5** | 1 jour | **Security Agent** | Sécurité & gestion d'erreurs |
| **Phase 6** | 2 jours | **Enhancement Agent** | Fonctionnalités manquantes |
| **Phase 7** | 1 jour | **Quality Agent** | Qualité & documentation |

**Durée totale:** ~12 jours ouvrés (2.5 semaines)

---

## Phase 0: Setup de l'Infrastructure de Tests (2h)

### Agent: **Setup Agent**

**Profil:**
- Spécialiste DevOps/Testing
- Expert pytest, fixtures, mocking
- Connaissance CI/CD

### Objectifs
1. ✅ Configurer l'environnement de tests
2. ✅ Créer la structure de répertoires
3. ✅ Configurer pytest avec coverage
4. ✅ Créer les fixtures de base
5. ✅ Vérifier que les tests s'exécutent

### Tâches TDD

#### Task 0.1: Créer la structure de tests
```bash
tests/
├── __init__.py
├── conftest.py                    # Fixtures globales
├── unit/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── test_project_entity.py
│   │   └── test_project_service.py
│   └── adapters/
│       └── __init__.py
├── integration/
│   ├── __init__.py
│   └── test_repository.py
└── e2e/
    ├── __init__.py
    └── test_api.py
```

#### Task 0.2: Configuration pytest
**Fichier:** `tests/conftest.py`
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.adapters.secondary.repositories.sqlalchemy_project_repository import Base

@pytest.fixture(scope="session")
def test_engine():
    """Engine SQLite en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Session DB avec rollback automatique."""
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_repository():
    """Mock du repository pour tests unitaires."""
    from unittest.mock import Mock
    from src.ports.secondary.project_repository import ProjectRepositoryPort
    return Mock(spec=ProjectRepositoryPort)
```

#### Task 0.3: Test canary (test de fumée)
**Fichier:** `tests/test_setup.py`
```python
def test_imports():
    """Vérifier que les imports fonctionnent."""
    from src.domain.entities.project import Project
    from src.domain.services.project_service import ProjectService
    from src.ports.primary.project_use_cases import ProjectUseCasesPort
    assert True

def test_database_fixture(db_session):
    """Vérifier que la fixture DB fonctionne."""
    assert db_session is not None
```

**Commande:**
```bash
uv run pytest tests/test_setup.py -v
```

**Résultat attendu:** ✅ 2 tests passent

#### Task 0.4: Configuration coverage
**Fichier:** `pyproject.toml` (déjà configuré, vérifier)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "--verbose",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]
```

### Livrables Phase 0
- [ ] Structure tests/ créée
- [ ] conftest.py avec fixtures
- [ ] Test canary passant
- [ ] Coverage configuré
- [ ] Documentation: TESTING.md

---

## Phase 1: Correction des Bugs Critiques (1 jour)

### Agent: **Critical Fix Agent**

**Profil:**
- Expert debugging
- Connaissance SQLAlchemy, FastAPI
- Expérience bugs production

### Problèmes à Corriger

#### Bug #1: Fuite de sessions DB (CRITIQUE 🔥)
#### Bug #3: Encodage emojis Windows (BLOQUANT)

### Cycle TDD

#### 1.1 Bug Sessions DB

**RED: Écrire le test qui échoue**

**Fichier:** `tests/unit/test_di_container.py`
```python
def test_db_session_is_closed_after_use():
    """La session doit être fermée après utilisation."""
    from src.di_container import get_db_session

    # Simuler l'utilisation dans une requête
    session_gen = get_db_session()
    session = next(session_gen)

    assert session.is_active  # Session active

    # Simuler la fin de la requête
    try:
        next(session_gen)
    except StopIteration:
        pass

    assert not session.is_active  # Session fermée

def test_multiple_requests_dont_leak_connections():
    """Plusieurs requêtes ne doivent pas accumuler les connexions."""
    from src.di_container import engine

    initial_pool_size = engine.pool.size()

    # Simuler 10 requêtes
    for _ in range(10):
        session_gen = get_db_session()
        session = next(session_gen)
        # Utiliser la session
        try:
            next(session_gen)
        except StopIteration:
            pass

    # Le pool ne doit pas avoir grossi
    assert engine.pool.size() == initial_pool_size
```

**Exécuter:** `uv run pytest tests/unit/test_di_container.py -v`
**Résultat attendu:** ❌ FAILED (le test échoue, c'est normal en TDD)

---

**GREEN: Faire passer le test**

**Fichier:** `src/di_container.py` (CORRIGER)
```python
def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency FastAPI avec gestion automatique de session.

    Yields:
        Session SQLAlchemy qui sera fermée automatiquement
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # ✅ Fermeture garantie
```

**Exécuter:** `uv run pytest tests/unit/test_di_container.py -v`
**Résultat attendu:** ✅ PASSED

---

**REFACTOR: Améliorer le code**

- Ajouter docstring complète
- Ajouter logging de debug
- Vérifier pas d'autres fuites

---

#### 1.2 Bug Encodage Windows

**RED: Écrire le test qui échoue**

**Fichier:** `tests/unit/test_di_container.py`
```python
import sys
from io import StringIO

def test_di_container_loads_without_unicode_error():
    """Le DI container doit charger sans erreur d'encodage."""
    # Simuler une console Windows non-UTF8
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    sys.stdout.encoding = 'cp1252'  # Encoding Windows

    try:
        # Recharger le module
        import importlib
        import src.di_container
        importlib.reload(src.di_container)
        # Si on arrive ici, pas d'erreur
        assert True
    except UnicodeEncodeError:
        pytest.fail("UnicodeEncodeError lors du chargement")
    finally:
        sys.stdout = old_stdout
```

**Exécuter:** `uv run pytest tests/unit/test_di_container.py::test_di_container_loads_without_unicode_error -v`
**Résultat attendu:** ❌ FAILED

---

**GREEN: Faire passer le test**

**Fichier:** `src/di_container.py` (CORRIGER)
```python
# Remplacer les emojis par du texte simple
print(f"[DATABASE] Using: {DATABASE_URL.split('://')[0].upper()}")
# ...
print("[DATABASE] Tables created/verified successfully")
```

**Alternative avec gestion d'erreur:**
```python
def safe_print(message: str) -> None:
    """Print avec gestion des erreurs d'encodage."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback sans emojis
        print(message.encode('ascii', 'ignore').decode('ascii'))

safe_print(f"📊 Utilisation de la base de données: {DATABASE_URL.split('://')[0].upper()}")
```

**Exécuter:** `uv run pytest tests/unit/test_di_container.py::test_di_container_loads_without_unicode_error -v`
**Résultat attendu:** ✅ PASSED

---

**REFACTOR:**
- Créer un module `src/utils/logging.py` pour centraliser
- Utiliser un vrai logger au lieu de print()

### Livrables Phase 1
- [ ] Test sessions DB passant
- [ ] Test encodage passant
- [ ] Code corrigé
- [ ] Documentation des fixes
- [ ] Rapport: CRITICAL_FIXES.md

---

## Phase 2: Conformité Architecture Hexagonale (2 jours)

### Agent: **Architecture Agent**

**Profil:**
- Expert architecture hexagonale
- Connaissance design patterns
- Expérience refactoring large scale

### Problèmes à Corriger

#### Bug #2: Service n'implémente pas l'interface ProjectUseCasesPort

### Cycle TDD

#### 2.1 Interface ProjectUseCasesPort

**RED: Écrire le test qui échoue**

**Fichier:** `tests/unit/domain/test_project_service.py`
```python
from src.domain.services.project_service import ProjectService
from src.ports.primary.project_use_cases import ProjectUseCasesPort

def test_project_service_implements_use_cases_port():
    """Le service doit implémenter l'interface ProjectUseCasesPort."""
    assert issubclass(ProjectService, ProjectUseCasesPort)

def test_project_service_has_all_interface_methods(mock_repository):
    """Le service doit avoir toutes les méthodes de l'interface."""
    service = ProjectService(mock_repository)

    # Vérifier que toutes les méthodes abstraites sont implémentées
    for method_name in dir(ProjectUseCasesPort):
        if not method_name.startswith('_'):
            assert hasattr(service, method_name)
            assert callable(getattr(service, method_name))
```

**Exécuter:** `uv run pytest tests/unit/domain/test_project_service.py -v`
**Résultat attendu:** ❌ FAILED

---

**GREEN: Faire passer le test**

**Fichier:** `src/domain/services/project_service.py` (CORRIGER)
```python
from src.ports.primary.project_use_cases import ProjectUseCasesPort

class ProjectService(ProjectUseCasesPort):  # ✅ Hérite de l'interface
    """
    Service métier pour la gestion des projets.
    Implémente ProjectUseCasesPort (port primaire).
    """

    def __init__(self, project_repository: ProjectRepositoryPort):
        self._repository = project_repository

    # Les méthodes restent identiques
    def create_project(...) -> Project:
        ...

    def get_project(...) -> Project:
        ...
```

**Exécuter:** `uv run pytest tests/unit/domain/test_project_service.py -v`
**Résultat attendu:** ✅ PASSED

---

**REFACTOR:**
- Ajouter validation mypy avec `--strict`
- Documenter le contrat d'interface

#### 2.2 Type Hints Complets

**RED: Test avec mypy**

**Fichier:** `tests/test_type_checking.py`
```python
import subprocess

def test_mypy_strict_passes():
    """Le code doit passer mypy en mode strict."""
    result = subprocess.run(
        ["mypy", "src/", "--strict"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"mypy errors:\n{result.stdout}"
```

**Exécuter:** `uv run pytest tests/test_type_checking.py -v`
**Résultat attendu:** ❌ FAILED (beaucoup d'erreurs de type)

---

**GREEN: Corriger les types**

**Fichier:** `src/ports/primary/project_use_cases.py` (CORRIGER)
```python
from abc import ABC, abstractmethod
from datetime import date  # ✅ Import ajouté
from typing import Optional
from src.domain.entities.project import Project

class ProjectUseCasesPort(ABC):
    """Interface des cas d'usage pour les projets."""

    @abstractmethod
    def create_project(
        self,
        name: str,
        description: str,
        start_date: date,  # ✅ Type ajouté
        end_date: date,    # ✅ Type ajouté
        budget: float,
        comment: Optional[str],  # ✅ Type ajouté
        manager_id: int
    ) -> Project:
        """Crée un nouveau projet."""
        pass

    @abstractmethod
    def get_project(self, project_id: int) -> Project:
        """Récupère un projet par son ID."""
        pass
```

**Répéter pour tous les fichiers:**
- `src/domain/services/project_service.py`
- `src/adapters/secondary/repositories/sqlalchemy_project_repository.py`

**Exécuter:** `uv run pytest tests/test_type_checking.py -v`
**Résultat attendu:** ✅ PASSED

### Livrables Phase 2
- [ ] Service implémente l'interface
- [ ] Type hints complets (mypy --strict OK)
- [ ] Tests d'architecture passants
- [ ] Diagramme UML mis à jour
- [ ] Rapport: ARCHITECTURE_COMPLIANCE.md

---

## Phase 3: Tests du Domaine Métier (2 jours)

### Agent: **Domain Agent**

**Profil:**
- Expert domain-driven design (DDD)
- Connaissance règles métier
- Expérience tests unitaires

### Objectif
Tester exhaustivement le domaine (entité + service) avec couverture 100%

### Cycle TDD

#### 3.1 Tests de l'Entité Project

**RED: Tests des règles métier**

**Fichier:** `tests/unit/domain/test_project_entity.py`
```python
import pytest
from datetime import date, timedelta
from src.domain.entities.project import Project

class TestProjectValidation:
    """Tests des validations de l'entité Project."""

    def test_project_creation_valid(self):
        """Un projet valide doit être créé sans erreur."""
        project = Project(
            id=None,
            name="Projet Test",
            description="Description test",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment="Commentaire",
            manager_id=1
        )
        assert project.name == "Projet Test"
        assert project.budget == 1000.0

    def test_project_rejects_empty_name(self):
        """Le nom vide doit être rejeté."""
        with pytest.raises(ValueError, match="nom du projet ne peut pas être vide"):
            Project(
                id=None,
                name="",  # ❌ Invalide
                description="Test",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=1000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_whitespace_only_name(self):
        """Un nom avec seulement des espaces doit être rejeté."""
        with pytest.raises(ValueError, match="nom du projet ne peut pas être vide"):
            Project(
                id=None,
                name="   ",  # ❌ Invalide
                description="Test",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=1000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_negative_budget(self):
        """Un budget négatif doit être rejeté."""
        with pytest.raises(ValueError, match="budget doit être positif"):
            Project(
                id=None,
                name="Test",
                description="Test",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=-100.0,  # ❌ Invalide
                comment=None,
                manager_id=1
            )

    def test_project_rejects_zero_budget(self):
        """Un budget de zéro doit être rejeté."""
        with pytest.raises(ValueError, match="budget doit être positif"):
            Project(
                id=None,
                name="Test",
                description="Test",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=0.0,  # ❌ Invalide
                comment=None,
                manager_id=1
            )

    def test_project_rejects_end_date_before_start_date(self):
        """La date de fin avant la date de début doit être rejetée."""
        with pytest.raises(ValueError, match="date de fin doit être après"):
            Project(
                id=None,
                name="Test",
                description="Test",
                start_date=date(2025, 12, 31),
                end_date=date(2025, 1, 1),  # ❌ Invalide
                budget=1000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_equal_dates(self):
        """Les dates identiques doivent être rejetées."""
        with pytest.raises(ValueError, match="date de fin doit être après"):
            Project(
                id=None,
                name="Test",
                description="Test",
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 1),  # ❌ Invalide
                budget=1000.0,
                comment=None,
                manager_id=1
            )


class TestProjectBusinessLogic:
    """Tests de la logique métier de l'entité."""

    def test_project_is_active_when_in_date_range(self):
        """Un projet en cours doit être actif."""
        project = Project(
            id=1,
            name="Projet Actif",
            description="Test",
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=10),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.is_active() is True

    def test_project_is_not_active_before_start_date(self):
        """Un projet pas encore commencé n'est pas actif."""
        project = Project(
            id=1,
            name="Projet Futur",
            description="Test",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.is_active() is False

    def test_project_is_not_active_after_end_date(self):
        """Un projet terminé n'est pas actif."""
        project = Project(
            id=1,
            name="Projet Terminé",
            description="Test",
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=10),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.is_active() is False

    def test_days_remaining_positive(self):
        """Jours restants correct pour projet en cours."""
        project = Project(
            id=1,
            name="Test",
            description="Test",
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.days_remaining() == 15

    def test_days_remaining_zero_after_end(self):
        """Jours restants = 0 pour projet terminé."""
        project = Project(
            id=1,
            name="Test",
            description="Test",
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=10),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.days_remaining() == 0

    def test_days_remaining_on_last_day(self):
        """Dernier jour du projet."""
        project = Project(
            id=1,
            name="Test",
            description="Test",
            start_date=date.today() - timedelta(days=10),
            end_date=date.today(),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        assert project.days_remaining() == 0
```

**Exécuter:** `uv run pytest tests/unit/domain/test_project_entity.py -v --cov=src/domain/entities/project`
**Résultat attendu:**
- Si le code est correct: ✅ Tous les tests passent
- Si bugs découverts: ❌ Certains tests échouent → corriger le code

---

**GREEN: Corriger si nécessaire**

Si des tests échouent, corriger `src/domain/entities/project.py`

---

**REFACTOR:**
- Ajouter edge cases supplémentaires
- Refactoriser les validations si répétitif

#### 3.2 Tests du Service Métier

**RED: Tests avec mock du repository**

**Fichier:** `tests/unit/domain/test_project_service.py`
```python
import pytest
from datetime import date
from unittest.mock import Mock
from src.domain.services.project_service import ProjectService
from src.domain.entities.project import Project
from src.ports.secondary.project_repository import ProjectRepositoryPort

@pytest.fixture
def mock_repository():
    """Mock du repository."""
    return Mock(spec=ProjectRepositoryPort)

@pytest.fixture
def service(mock_repository):
    """Service avec repository mocké."""
    return ProjectService(mock_repository)


class TestCreateProject:
    """Tests du cas d'usage create_project."""

    def test_create_project_success(self, service, mock_repository):
        """Créer un projet avec succès."""
        # Arrange
        mock_repository.exists_by_name.return_value = False
        mock_repository.save.return_value = Project(
            id=1,
            name="Nouveau Projet",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment="Test",
            manager_id=1
        )

        # Act
        result = service.create_project(
            name="Nouveau Projet",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment="Test",
            manager_id=1
        )

        # Assert
        assert result.id == 1
        assert result.name == "Nouveau Projet"
        mock_repository.exists_by_name.assert_called_once_with("Nouveau Projet")
        mock_repository.save.assert_called_once()

    def test_create_project_rejects_duplicate_name(self, service, mock_repository):
        """Ne pas créer un projet avec un nom existant."""
        # Arrange
        mock_repository.exists_by_name.return_value = True  # Nom existe déjà

        # Act & Assert
        with pytest.raises(ValueError, match="existe déjà"):
            service.create_project(
                name="Projet Existant",
                description="Description",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=1000.0,
                comment=None,
                manager_id=1
            )

        # Vérifier que save n'a pas été appelé
        mock_repository.save.assert_not_called()

    def test_create_project_validates_entity_rules(self, service, mock_repository):
        """Les règles de l'entité doivent être validées."""
        # Arrange
        mock_repository.exists_by_name.return_value = False

        # Act & Assert - Budget négatif
        with pytest.raises(ValueError, match="budget doit être positif"):
            service.create_project(
                name="Test",
                description="Description",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=-100.0,  # Invalide
                comment=None,
                manager_id=1
            )


class TestGetProject:
    """Tests du cas d'usage get_project."""

    def test_get_project_success(self, service, mock_repository):
        """Récupérer un projet existant."""
        # Arrange
        expected_project = Project(
            id=1,
            name="Projet Test",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        mock_repository.find_by_id.return_value = expected_project

        # Act
        result = service.get_project(1)

        # Assert
        assert result == expected_project
        mock_repository.find_by_id.assert_called_once_with(1)

    def test_get_project_not_found(self, service, mock_repository):
        """Erreur si projet n'existe pas."""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="n'existe pas"):
            service.get_project(999)
```

**Exécuter:** `uv run pytest tests/unit/domain/test_project_service.py -v --cov=src/domain/services`
**Résultat attendu:** ✅ Tous les tests passent

### Livrables Phase 3
- [ ] Tests entité: 100% couverture
- [ ] Tests service: 100% couverture
- [ ] Tous les tests passent
- [ ] Rapport: DOMAIN_TESTING.md
- [ ] Couverture domaine: 100%

---

## Phase 4: Tests des Adapters (2 jours)

### Agent: **Integration Agent**

**Profil:**
- Expert tests d'intégration
- Connaissance SQLAlchemy, FastAPI
- Expérience tests de BD

### Objectif
Tester les adapters (repository, router) avec vrais composants

#### 4.1 Tests du Repository SQLAlchemy

**RED: Tests d'intégration avec base de données**

**Fichier:** `tests/integration/test_repository.py`
```python
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
    Base,
    ProjectModel
)
from src.domain.entities.project import Project

@pytest.fixture(scope="function")
def db_session():
    """Session de base de données en mémoire pour chaque test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()

@pytest.fixture
def repository(db_session):
    """Repository avec session de test."""
    return SQLAlchemyProjectRepository(db_session)


class TestRepositorySave:
    """Tests de la méthode save."""

    def test_save_project_generates_id(self, repository):
        """Sauvegarder un projet doit générer un ID."""
        # Arrange
        project = Project(
            id=None,  # Pas d'ID
            name="Nouveau Projet",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment="Test",
            manager_id=1
        )

        # Act
        saved = repository.save(project)

        # Assert
        assert saved.id is not None
        assert saved.id > 0
        assert saved.name == "Nouveau Projet"

    def test_save_project_persists_data(self, repository, db_session):
        """Les données doivent être persistées en base."""
        # Arrange
        project = Project(
            id=None,
            name="Test Persistance",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=5000.0,
            comment="Commentaire",
            manager_id=2
        )

        # Act
        saved = repository.save(project)

        # Assert - Vérifier en base directement
        db_project = db_session.query(ProjectModel).filter_by(id=saved.id).first()
        assert db_project is not None
        assert db_project.name == "Test Persistance"
        assert db_project.budget == 5000.0
        assert db_project.manager_id == 2


class TestRepositoryFindById:
    """Tests de la méthode find_by_id."""

    def test_find_by_id_returns_project(self, repository, db_session):
        """find_by_id doit retourner le projet correct."""
        # Arrange - Créer un projet en base
        db_project = ProjectModel(
            name="Projet Test",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=3000.0,
            comment="Test",
            manager_id=1
        )
        db_session.add(db_project)
        db_session.commit()

        # Act
        found = repository.find_by_id(db_project.id)

        # Assert
        assert found is not None
        assert found.id == db_project.id
        assert found.name == "Projet Test"
        assert found.budget == 3000.0

    def test_find_by_id_returns_none_if_not_found(self, repository):
        """find_by_id doit retourner None si projet inexistant."""
        # Act
        found = repository.find_by_id(9999)

        # Assert
        assert found is None


class TestRepositoryExistsByName:
    """Tests de la méthode exists_by_name."""

    def test_exists_by_name_returns_true_if_exists(self, repository, db_session):
        """exists_by_name doit retourner True si le nom existe."""
        # Arrange
        db_project = ProjectModel(
            name="Projet Unique",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        db_session.add(db_project)
        db_session.commit()

        # Act
        exists = repository.exists_by_name("Projet Unique")

        # Assert
        assert exists is True

    def test_exists_by_name_returns_false_if_not_exists(self, repository):
        """exists_by_name doit retourner False si le nom n'existe pas."""
        # Act
        exists = repository.exists_by_name("Projet Inexistant")

        # Assert
        assert exists is False


class TestRepositoryFindAll:
    """Tests de la méthode find_all."""

    def test_find_all_returns_empty_list_when_no_projects(self, repository):
        """find_all doit retourner une liste vide si pas de projets."""
        # Act
        projects = repository.find_all()

        # Assert
        assert projects == []

    def test_find_all_returns_all_projects(self, repository, db_session):
        """find_all doit retourner tous les projets."""
        # Arrange - Créer 3 projets
        for i in range(3):
            db_project = ProjectModel(
                name=f"Projet {i}",
                description="Description",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                budget=1000.0 * (i + 1),
                comment=None,
                manager_id=1
            )
            db_session.add(db_project)
        db_session.commit()

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 3
        assert all(isinstance(p, Project) for p in projects)


class TestRepositoryDelete:
    """Tests de la méthode delete."""

    def test_delete_removes_project(self, repository, db_session):
        """delete doit supprimer le projet."""
        # Arrange
        db_project = ProjectModel(
            name="Projet à Supprimer",
            description="Description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000.0,
            comment=None,
            manager_id=1
        )
        db_session.add(db_project)
        db_session.commit()
        project_id = db_project.id

        # Act
        result = repository.delete(project_id)

        # Assert
        assert result is True
        assert db_session.query(ProjectModel).filter_by(id=project_id).first() is None

    def test_delete_returns_false_if_not_found(self, repository):
        """delete doit retourner False si projet inexistant."""
        # Act
        result = repository.delete(9999)

        # Assert
        assert result is False
```

**Exécuter:** `uv run pytest tests/integration/test_repository.py -v --cov=src/adapters/secondary`
**Résultat attendu:** ✅ Tous les tests passent

#### 4.2 Tests E2E de l'API

**RED: Tests de bout en bout**

**Fichier:** `tests/e2e/test_api.py`
```python
import pytest
from fastapi.testclient import TestClient
from datetime import date

@pytest.fixture(scope="module")
def client():
    """Client de test FastAPI."""
    from src.main import app
    return TestClient(app)


class TestCreateProjectEndpoint:
    """Tests du endpoint POST /api/projects."""

    def test_create_project_success(self, client):
        """Créer un projet via l'API doit retourner 201."""
        # Arrange
        payload = {
            "name": f"Projet API Test {date.today().isoformat()}",
            "description": "Test via API",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "budget": 10000.0,
            "comment": "Test E2E",
            "manager_id": 1
        }

        # Act
        response = client.post("/api/projects", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["budget"] == payload["budget"]
        assert data["id"] is not None
        assert "is_active" in data
        assert "days_remaining" in data

    def test_create_project_duplicate_name_returns_400(self, client):
        """Créer un projet avec nom existant doit retourner 400."""
        # Arrange - Créer un projet
        unique_name = f"Projet Unique {date.today().isoformat()}"
        payload = {
            "name": unique_name,
            "description": "Premier projet",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "budget": 1000.0,
            "comment": None,
            "manager_id": 1
        }
        client.post("/api/projects", json=payload)

        # Act - Tenter de créer un doublon
        response = client.post("/api/projects", json=payload)

        # Assert
        assert response.status_code == 400
        assert "existe déjà" in response.json()["detail"]

    def test_create_project_invalid_budget_returns_422(self, client):
        """Budget négatif doit retourner 422 (validation Pydantic)."""
        # Arrange
        payload = {
            "name": "Projet Budget Invalide",
            "description": "Test",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "budget": -1000.0,  # Invalide
            "comment": None,
            "manager_id": 1
        }

        # Act
        response = client.post("/api/projects", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_project_invalid_dates_returns_400(self, client):
        """Dates invalides doivent retourner 400."""
        # Arrange
        payload = {
            "name": "Projet Dates Invalides",
            "description": "Test",
            "start_date": "2025-12-31",
            "end_date": "2025-01-01",  # Fin avant début
            "budget": 1000.0,
            "comment": None,
            "manager_id": 1
        }

        # Act
        response = client.post("/api/projects", json=payload)

        # Assert
        assert response.status_code == 400


class TestGetProjectEndpoint:
    """Tests du endpoint GET /api/projects/{id}."""

    def test_get_project_success(self, client):
        """Récupérer un projet existant doit retourner 200."""
        # Arrange - Créer un projet
        create_payload = {
            "name": f"Projet GET Test {date.today().isoformat()}",
            "description": "Test GET",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "budget": 5000.0,
            "comment": "Test",
            "manager_id": 1
        }
        create_response = client.post("/api/projects", json=create_payload)
        project_id = create_response.json()["id"]

        # Act
        response = client.get(f"/api/projects/{project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == create_payload["name"]

    def test_get_project_not_found_returns_404(self, client):
        """Récupérer un projet inexistant doit retourner 404."""
        # Act
        response = client.get("/api/projects/99999")

        # Assert
        assert response.status_code == 404


class TestAPIDocumentation:
    """Tests de la documentation auto-générée."""

    def test_openapi_schema_accessible(self, client):
        """Le schéma OpenAPI doit être accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

    def test_swagger_ui_accessible(self, client):
        """Swagger UI doit être accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self, client):
        """ReDoc doit être accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
```

**Exécuter:** `uv run pytest tests/e2e/test_api.py -v`
**Résultat attendu:** ✅ Tous les tests passent

### Livrables Phase 4
- [ ] Tests repository: 100% couverture
- [ ] Tests API E2E complets
- [ ] Tous les tests passent
- [ ] Rapport: INTEGRATION_TESTING.md
- [ ] Couverture adapters: >90%

---

## Phase 5: Sécurité et Gestion d'Erreurs (1 jour)

### Agent: **Security Agent**

**Profil:**
- Expert sécurité applicative
- Connaissance OWASP
- Expérience gestion d'erreurs

### Objectif
Corriger Bug #4 et améliorer la sécurité

#### 5.1 Exceptions Métier Personnalisées

**RED: Tests avec exceptions custom**

**Fichier:** `tests/unit/domain/test_exceptions.py`
```python
import pytest
from src.domain.exceptions import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    DomainValidationError
)

def test_project_already_exists_error():
    """Exception pour projet existant."""
    error = ProjectAlreadyExistsError("Projet Test")
    assert "Projet Test" in str(error)
    assert isinstance(error, DomainValidationError)

def test_project_not_found_error():
    """Exception pour projet non trouvé."""
    error = ProjectNotFoundError(123)
    assert "123" in str(error)
```

**Exécuter:** `uv run pytest tests/unit/domain/test_exceptions.py -v`
**Résultat attendu:** ❌ FAILED (module n'existe pas)

---

**GREEN: Créer les exceptions**

**Fichier:** `src/domain/exceptions.py` (NOUVEAU)
```python
"""
Exceptions métier du domaine.
Ces exceptions représentent des erreurs métier, pas des erreurs techniques.
"""

class DomainError(Exception):
    """Exception de base pour toutes les erreurs du domaine."""
    pass


class DomainValidationError(DomainError):
    """Erreur de validation des règles métier."""
    pass


class ProjectAlreadyExistsError(DomainValidationError):
    """Un projet avec ce nom existe déjà."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(f"Un projet avec le nom '{project_name}' existe déjà")


class ProjectNotFoundError(DomainError):
    """Le projet demandé n'existe pas."""

    def __init__(self, project_id: int):
        self.project_id = project_id
        super().__init__(f"Le projet avec l'ID {project_id} n'existe pas")
```

**Modifier:** `src/domain/services/project_service.py`
```python
from src.domain.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError

class ProjectService(ProjectUseCasesPort):

    def create_project(...) -> Project:
        if self._repository.exists_by_name(name):
            raise ProjectAlreadyExistsError(name)  # ✅ Exception typée
        # ...

    def get_project(self, project_id: int) -> Project:
        project = self._repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)  # ✅ Exception typée
        return project
```

**Modifier:** `src/adapters/primary/fastapi/routers/projects_router.py`
```python
from src.domain.exceptions import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    DomainValidationError
)
import logging

logger = logging.getLogger(__name__)

@router.post(...)
def create_project(...):
    try:
        project = use_cases.create_project(...)
        return ProjectResponse(...)

    except ProjectAlreadyExistsError as e:
        # Conflit - 409
        raise HTTPException(status_code=409, detail=str(e))

    except DomainValidationError as e:
        # Validation métier - 400
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Erreur inattendue - 500
        logger.error(f"Unexpected error creating project", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne s'est produite"  # ✅ Message générique
        )
```

**Exécuter:** `uv run pytest tests/ -v`
**Résultat attendu:** ✅ Tous les tests passent

### Livrables Phase 5
- [ ] Exceptions métier créées
- [ ] Gestion d'erreurs sécurisée
- [ ] Logging structuré
- [ ] Tests de sécurité
- [ ] Rapport: SECURITY_IMPROVEMENTS.md

---

## Phase 6: Fonctionnalités Manquantes (2 jours)

### Agent: **Enhancement Agent**

**Profil:**
- Full-stack developer
- Expert CRUD operations
- Connaissance pagination

### Objectif
Ajouter les endpoints manquants (PUT, DELETE, GET list)

#### 6.1 Endpoint PUT (Update)

**RED: Tests du update**

**Fichier:** `tests/e2e/test_update_project.py`
```python
def test_update_project_success(client):
    """Mettre à jour un projet doit retourner 200."""
    # Créer un projet
    create_response = client.post("/api/projects", json={...})
    project_id = create_response.json()["id"]

    # Mettre à jour
    update_payload = {..., "budget": 20000.0}
    response = client.put(f"/api/projects/{project_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["budget"] == 20000.0
```

**GREEN: Implémenter le endpoint**

(Suivre le cycle TDD complet)

#### 6.2 Endpoint DELETE

**RED → GREEN → REFACTOR**

#### 6.3 Endpoint GET avec Pagination

**RED → GREEN → REFACTOR**

### Livrables Phase 6
- [ ] PUT /api/projects/{id} implémenté
- [ ] DELETE /api/projects/{id} implémenté
- [ ] GET /api/projects avec pagination
- [ ] Tests E2E pour tous les endpoints
- [ ] Documentation Swagger mise à jour

---

## Phase 7: Qualité et Documentation (1 jour)

### Agent: **Quality Agent**

**Profil:**
- QA engineer
- Expert documentation technique
- Connaissance CI/CD

### Objectif
Finaliser la qualité et la documentation

### Tâches

#### 7.1 Couverture de Tests
- [ ] Atteindre 90%+ de couverture globale
- [ ] Identifier les lignes non testées
- [ ] Ajouter tests manquants

#### 7.2 Configuration CI/CD

**Fichier:** `.github/workflows/ci.yml` (NOUVEAU)
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest tests/ -v --cov=src --cov-report=xml

      - name: Run mypy
        run: uv run mypy src/ --strict

      - name: Run ruff
        run: uv run ruff check src/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

#### 7.3 Documentation

- [ ] Mettre à jour README.md
- [ ] Créer TESTING.md (guide des tests)
- [ ] Créer CONTRIBUTING.md
- [ ] Documenter les changements dans CHANGELOG.md

### Livrables Phase 7
- [ ] Couverture >90%
- [ ] CI/CD configuré
- [ ] Documentation complète
- [ ] Rapport final: REFACTORING_REPORT.md

---

## Résumé des Agents à Recruter

| Agent | Compétences Clés | Responsabilités |
|-------|------------------|----------------|
| **Setup Agent** | pytest, fixtures, DevOps | Infra tests |
| **Critical Fix Agent** | Debugging, SQLAlchemy | Bugs critiques |
| **Architecture Agent** | Hexagonal arch, DDD | Conformité archi |
| **Domain Agent** | Domain-Driven Design | Tests domaine |
| **Integration Agent** | Integration testing | Tests adapters |
| **Security Agent** | OWASP, error handling | Sécurité |
| **Enhancement Agent** | Full-stack, CRUD | Nouvelles features |
| **Quality Agent** | QA, documentation | Qualité finale |

---

## Métriques de Succès

### Avant Refactoring
- ❌ 0% de couverture de tests
- ❌ Bugs critiques (sessions, encoding)
- ❌ Violation archi hexagonale
- ❌ Pas de type checking
- ❌ Gestion d'erreurs dangereuse

### Après Refactoring (Cible)
- ✅ >90% de couverture de tests
- ✅ Tous les bugs critiques corrigés
- ✅ Architecture 100% conforme
- ✅ mypy --strict passing
- ✅ Gestion d'erreurs sécurisée
- ✅ Fonctionnalités CRUD complètes
- ✅ CI/CD configuré
- ✅ Documentation à jour

---

## Commandes Utiles

### Lancer tous les tests
```bash
uv run pytest tests/ -v --cov=src --cov-report=html
```

### Tests par catégorie
```bash
# Tests unitaires uniquement
uv run pytest tests/unit/ -v

# Tests d'intégration
uv run pytest tests/integration/ -v

# Tests E2E
uv run pytest tests/e2e/ -v
```

### Type checking
```bash
uv run mypy src/ --strict
```

### Linting
```bash
uv run ruff check src/
uv run black src/ --check
```

### Générer le rapport de couverture
```bash
uv run pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html
```

---

## Conclusion

Ce plan TDD garantit:
1. **Qualité:** Chaque changement est testé
2. **Sécurité:** Tests avant code
3. **Maintenabilité:** Tests documentent le comportement
4. **Confiance:** Refactoring sûr grâce aux tests

**Prêt à recruter les agents et démarrer la Phase 0 !**
