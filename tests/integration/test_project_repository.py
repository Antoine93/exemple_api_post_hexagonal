"""
Integration tests for SQLAlchemy repository.

Tests the repository implementation with a real database (SQLite in-memory).
These tests verify that the repository correctly interacts with the database.
"""
import pytest
from datetime import date, datetime, timedelta

from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
    ProjectModel,
)
from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType


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
        assert saved_project.numero == sample_project.numero
        assert saved_project.nom == sample_project.nom
        assert saved_project.description == sample_project.description
        assert saved_project.date_debut == sample_project.date_debut
        assert saved_project.date_echeance == sample_project.date_echeance
        assert saved_project.type == sample_project.type
        assert saved_project.stade == sample_project.stade
        assert saved_project.commentaire == sample_project.commentaire
        assert saved_project.heures_planifiees == sample_project.heures_planifiees
        assert saved_project.heures_reelles == sample_project.heures_reelles
        assert saved_project.est_template == sample_project.est_template
        assert saved_project.projet_template_id == sample_project.projet_template_id
        assert saved_project.responsable_id == sample_project.responsable_id
        assert saved_project.entreprise_id == sample_project.entreprise_id
        assert saved_project.contact_id == sample_project.contact_id

        # Verify it's actually in the database
        project_model = db_session.query(ProjectModel).filter(
            ProjectModel.id == saved_project.id
        ).first()
        assert project_model is not None
        assert project_model.nom == sample_project.nom
        assert project_model.numero == sample_project.numero


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
        assert found_project.nom == sample_project_data["nom"]
        assert found_project.numero == sample_project_data["numero"]
        assert found_project.description == sample_project_data["description"]
        assert found_project.heures_planifiees == sample_project_data["heures_planifiees"]

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
        exists = repository.exists_by_name(sample_project_data["nom"])

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


class TestRepositoryExistsByNumero:
    """Test suite for repository exists_by_numero operations."""

    def test_exists_by_numero_returns_true_if_exists(self, db_session, create_project_in_db, sample_project_data):
        """Test that exists_by_numero() returns True for existing project numero."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        create_project_in_db(sample_project_data)

        # Act
        exists = repository.exists_by_numero(sample_project_data["numero"])

        # Assert
        assert exists is True

    def test_exists_by_numero_returns_false_if_not_exists(self, db_session):
        """Test that exists_by_numero() returns False for non-existent numero."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        exists = repository.exists_by_numero("PROJ-NONEXISTENT")

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
            "numero": "PROJ-ALPHA",
            "nom": "Project Alpha",
            "description": "First project",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.INTERNAL.value,
            "stade": "En cours",
            "commentaire": "Comment 1",
            "heures_planifiees": 100.0,
            "heures_reelles": 20.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None,
        }

        project2_data = {
            "numero": "PROJ-BETA",
            "nom": "Project Beta",
            "description": "Second project",
            "date_debut": today,
            "date_echeance": today + timedelta(days=60),
            "type": ProjectType.EXTERNAL.value,
            "stade": "Planifié",
            "commentaire": "Comment 2",
            "heures_planifiees": 200.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 2,
            "entreprise_id": 2,
            "contact_id": 1,
        }

        create_project_in_db(project1_data)
        create_project_in_db(project2_data)

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 2
        assert any(p.nom == "Project Alpha" for p in projects)
        assert any(p.nom == "Project Beta" for p in projects)

    def test_find_all_with_pagination(self, db_session, create_project_in_db):
        """Test that find_all() respects offset and limit parameters."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        # Create 5 projects
        for i in range(5):
            project_data = {
                "numero": f"PROJ-{i:03d}",
                "nom": f"Project {i}",
                "description": f"Description {i}",
                "date_debut": today,
                "date_echeance": today + timedelta(days=30),
                "type": ProjectType.INTERNAL.value,
                "stade": "En cours",
                "commentaire": f"Comment {i}",
                "heures_planifiees": 100.0,
                "heures_reelles": 0.0,
                "est_template": False,
                "projet_template_id": None,
                "responsable_id": 1,
                "entreprise_id": 1,
                "contact_id": None,
            }
            create_project_in_db(project_data)

        # Act
        projects_page1 = repository.find_all(offset=0, limit=2)
        projects_page2 = repository.find_all(offset=2, limit=2)

        # Assert
        assert len(projects_page1) == 2
        assert len(projects_page2) == 2


class TestRepositoryFindTemplates:
    """Test suite for repository find_templates operations."""

    def test_find_templates_returns_only_templates(self, db_session, create_project_in_db):
        """Test that find_templates() returns only projects marked as templates."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        # Create regular project
        regular_project_data = {
            "numero": "PROJ-REGULAR",
            "nom": "Regular Project",
            "description": "Not a template",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.INTERNAL.value,
            "stade": "En cours",
            "commentaire": "Regular",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None,
        }

        # Create template project
        template_project_data = {
            "numero": "TEMPLATE-001",
            "nom": "Template Project",
            "description": "This is a template",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.INTERNAL.value,
            "stade": "Template",
            "commentaire": "Template",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": True,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None,
        }

        create_project_in_db(regular_project_data)
        create_project_in_db(template_project_data)

        # Act
        templates = repository.find_templates()

        # Assert
        assert len(templates) == 1
        assert templates[0].nom == "Template Project"
        assert templates[0].est_template is True

    def test_find_templates_returns_empty_list_when_no_templates(self, db_session):
        """Test that find_templates() returns empty list when no templates exist."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)

        # Act
        templates = repository.find_templates()

        # Assert
        assert templates == []


class TestRepositoryUpdate:
    """Test suite for repository update operations."""

    def test_update_project_modifies_data(self, db_session, create_project_in_db, sample_project_data):
        """Test that update() correctly modifies project data."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        project_model = create_project_in_db(sample_project_data)

        # Create updated project entity
        updated_project = Project(
            id=project_model.id,
            numero=project_model.numero,
            nom="Updated Name",
            description="Updated Description",
            date_debut=sample_project_data["date_debut"],
            date_echeance=sample_project_data["date_echeance"],
            type=ProjectType.EXTERNAL,
            stade="Terminé",
            commentaire="Updated comment",
            heures_planifiees=150.0,
            heures_reelles=120.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=2,
            entreprise_id=2,
            contact_id=1,
            date_creation=datetime.now()
        )

        # Act
        result = repository.update(updated_project)

        # Assert
        assert result.nom == "Updated Name"
        assert result.description == "Updated Description"
        assert result.type == ProjectType.EXTERNAL
        assert result.stade == "Terminé"
        assert result.heures_planifiees == 150.0
        assert result.heures_reelles == 120.0
        assert result.responsable_id == 2


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


class TestRepositoryFindByTemplateId:
    """Test suite for repository find_by_template_id operations."""

    def test_find_by_template_id_returns_projects_created_from_template(self, db_session, create_project_in_db):
        """Test that find_by_template_id() returns all projects created from a template."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        # Create template
        template_data = {
            "numero": "TEMPLATE-001",
            "nom": "Template Project",
            "description": "Template",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.INTERNAL.value,
            "stade": "Template",
            "commentaire": "Template",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": True,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None,
        }
        template_model = create_project_in_db(template_data)

        # Create project from template
        project_from_template_data = {
            "numero": "PROJ-FROM-TEMPLATE",
            "nom": "Project From Template",
            "description": "Created from template",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.INTERNAL.value,
            "stade": "En cours",
            "commentaire": "From template",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": template_model.id,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None,
        }
        create_project_in_db(project_from_template_data)

        # Act
        projects_from_template = repository.find_by_template_id(template_model.id)

        # Assert
        assert len(projects_from_template) == 1
        assert projects_from_template[0].nom == "Project From Template"
        assert projects_from_template[0].projet_template_id == template_model.id


class TestRepositoryFindByEntreprise:
    """Test suite for repository find_by_entreprise operations."""

    def test_find_by_entreprise_returns_projects_for_entreprise(self, db_session, create_project_in_db):
        """Test that find_by_entreprise() returns all projects for a specific entreprise."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        # Create projects for entreprise 1
        for i in range(2):
            project_data = {
                "numero": f"PROJ-ENT1-{i}",
                "nom": f"Entreprise 1 Project {i}",
                "description": f"Description {i}",
                "date_debut": today,
                "date_echeance": today + timedelta(days=30),
                "type": ProjectType.INTERNAL.value,
                "stade": "En cours",
                "commentaire": "Comment",
                "heures_planifiees": 100.0,
                "heures_reelles": 0.0,
                "est_template": False,
                "projet_template_id": None,
                "responsable_id": 1,
                "entreprise_id": 1,
                "contact_id": None,
            }
            create_project_in_db(project_data)

        # Create project for entreprise 2
        project_data_ent2 = {
            "numero": "PROJ-ENT2-0",
            "nom": "Entreprise 2 Project",
            "description": "Description",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.EXTERNAL.value,
            "stade": "En cours",
            "commentaire": "Comment",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 2,
            "contact_id": None,
        }
        create_project_in_db(project_data_ent2)

        # Act
        projects_ent1 = repository.find_by_entreprise(1)
        projects_ent2 = repository.find_by_entreprise(2)

        # Assert
        assert len(projects_ent1) == 2
        assert len(projects_ent2) == 1
        assert all(p.entreprise_id == 1 for p in projects_ent1)
        assert all(p.entreprise_id == 2 for p in projects_ent2)


class TestRepositoryFindByResponsable:
    """Test suite for repository find_by_responsable operations."""

    def test_find_by_responsable_returns_projects_for_responsable(self, db_session, create_project_in_db):
        """Test that find_by_responsable() returns all projects for a specific responsable."""
        # Arrange
        repository = SQLAlchemyProjectRepository(db_session)
        today = date.today()

        # Create projects for responsable 1
        for i in range(3):
            project_data = {
                "numero": f"PROJ-RESP1-{i}",
                "nom": f"Responsable 1 Project {i}",
                "description": f"Description {i}",
                "date_debut": today,
                "date_echeance": today + timedelta(days=30),
                "type": ProjectType.INTERNAL.value,
                "stade": "En cours",
                "commentaire": "Comment",
                "heures_planifiees": 100.0,
                "heures_reelles": 0.0,
                "est_template": False,
                "projet_template_id": None,
                "responsable_id": 1,
                "entreprise_id": 1,
                "contact_id": None,
            }
            create_project_in_db(project_data)

        # Create project for responsable 2
        project_data_resp2 = {
            "numero": "PROJ-RESP2-0",
            "nom": "Responsable 2 Project",
            "description": "Description",
            "date_debut": today,
            "date_echeance": today + timedelta(days=30),
            "type": ProjectType.EXTERNAL.value,
            "stade": "En cours",
            "commentaire": "Comment",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 2,
            "entreprise_id": 1,
            "contact_id": None,
        }
        create_project_in_db(project_data_resp2)

        # Act
        projects_resp1 = repository.find_by_responsable(1)
        projects_resp2 = repository.find_by_responsable(2)

        # Assert
        assert len(projects_resp1) == 3
        assert len(projects_resp2) == 1
        assert all(p.responsable_id == 1 for p in projects_resp1)
        assert all(p.responsable_id == 2 for p in projects_resp2)
