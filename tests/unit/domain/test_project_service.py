"""
Unit tests for ProjectService.

Tests the domain service business logic with mocked repositories.
No real database - testing domain logic in isolation.
"""
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock

from src.domain.services.project_service import ProjectService
from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType
from src.domain.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from src.ports.primary.project_use_cases import ProjectUseCasesPort


@pytest.fixture
def mock_repository():
    """Mock du repository pour isoler les tests."""
    return Mock()


@pytest.fixture
def sample_project_data():
    """Données valides pour créer un projet."""
    today = date.today()
    return {
        "numero": "PROJ-001",
        "nom": "Test Project",
        "description": "A test project",
        "date_debut": today,
        "date_echeance": today + timedelta(days=30),
        "type": ProjectType.INTERNAL,
        "stade": "En cours",
        "commentaire": "Test comment",
        "heures_planifiees": 100.0,
        "heures_reelles": 0.0,
        "est_template": False,
        "projet_template_id": None,
        "responsable_id": 1,
        "entreprise_id": 1,
        "contact_id": None
    }


@pytest.fixture
def sample_project_with_id(sample_project_data):
    """Projet avec ID (simulant un projet sauvegardé)."""
    return Project(id=1, date_creation=datetime.now(), **sample_project_data)


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
        required_methods = [
            'create_project', 'get_project', 'update_project', 'delete_project',
            'list_projects', 'dupliquer_projet', 'sauvegarder_comme_template',
            'creer_depuis_template', 'find_templates', 'calculer_avancement',
            'calculer_ecart_temps'
        ]
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
        mock_repository.exists_by_numero.return_value = False
        mock_repository.exists_by_name.return_value = False

        expected_project = Project(id=1, date_creation=datetime.now(), **sample_project_data)
        mock_repository.save.return_value = expected_project

        # Act
        result = service.create_project(**sample_project_data)

        # Assert
        mock_repository.exists_by_numero.assert_called_once_with(sample_project_data["numero"])
        mock_repository.exists_by_name.assert_called_once_with(sample_project_data["nom"])
        mock_repository.save.assert_called_once()
        assert result.id == 1
        assert result.nom == sample_project_data["nom"]

    def test_create_project_rejects_duplicate_numero(self, mock_repository, sample_project_data):
        """Ne pas créer un projet avec un numéro existant."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_numero.return_value = True

        # Act & Assert
        with pytest.raises(ProjectAlreadyExistsError, match="numéro"):
            service.create_project(**sample_project_data)

        # Verify save was never called
        mock_repository.save.assert_not_called()

    def test_create_project_rejects_duplicate_name(self, mock_repository, sample_project_data):
        """Ne pas créer un projet avec un nom existant."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_numero.return_value = False
        mock_repository.exists_by_name.return_value = True

        # Act & Assert
        with pytest.raises(ProjectAlreadyExistsError, match="nom"):
            service.create_project(**sample_project_data)

        # Verify save was never called
        mock_repository.save.assert_not_called()

    def test_create_project_validates_entity_rules(self, mock_repository, sample_project_data):
        """Les règles de l'entité doivent être validées."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.exists_by_numero.return_value = False
        mock_repository.exists_by_name.return_value = False

        # Modifier les données pour invalider les dates
        sample_project_data["date_echeance"] = sample_project_data["date_debut"] - timedelta(days=1)

        # Act & Assert
        with pytest.raises(ValueError, match="date d'échéance doit être après"):
            service.create_project(**sample_project_data)

        # Verify save was never called
        mock_repository.save.assert_not_called()


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
        assert result.nom == sample_project_with_id.nom

    def test_get_project_not_found(self, mock_repository):
        """Erreur si projet n'existe pas."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            service.get_project(999)


class TestUpdateProject:
    """Tests du cas d'usage update_project."""

    def test_update_project_success(self, mock_repository, sample_project_with_id):
        """Mettre à jour un projet avec succès."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id
        # Mock that the new name doesn't exist yet
        mock_repository.exists_by_name.return_value = False

        updated_project = Project(
            id=1,
            numero=sample_project_with_id.numero,
            nom="Updated Name",
            description=sample_project_with_id.description,
            date_debut=sample_project_with_id.date_debut,
            date_echeance=sample_project_with_id.date_echeance,
            type=sample_project_with_id.type,
            stade=sample_project_with_id.stade,
            commentaire=sample_project_with_id.commentaire,
            heures_planifiees=sample_project_with_id.heures_planifiees,
            heures_reelles=sample_project_with_id.heures_reelles,
            est_template=sample_project_with_id.est_template,
            projet_template_id=sample_project_with_id.projet_template_id,
            responsable_id=sample_project_with_id.responsable_id,
            entreprise_id=sample_project_with_id.entreprise_id,
            contact_id=sample_project_with_id.contact_id,
            date_creation=sample_project_with_id.date_creation
        )
        mock_repository.update.return_value = updated_project

        # Act
        result = service.update_project(project_id=1, nom="Updated Name")

        # Assert
        mock_repository.update.assert_called_once()
        assert result.nom == "Updated Name"

    def test_update_project_not_found(self, mock_repository):
        """Erreur si projet à mettre à jour n'existe pas."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            service.update_project(project_id=999, nom="New Name")


class TestDeleteProject:
    """Tests du cas d'usage delete_project."""

    def test_delete_project_success(self, mock_repository, sample_project_with_id):
        """Supprimer un projet avec succès."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id
        mock_repository.delete.return_value = True

        # Act
        result = service.delete_project(1)

        # Assert
        mock_repository.delete.assert_called_once_with(1)
        assert result is True

    def test_delete_project_not_found(self, mock_repository):
        """Erreur si projet à supprimer n'existe pas."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            service.delete_project(999)


class TestListProjects:
    """Tests du cas d'usage list_projects."""

    def test_list_projects_success(self, mock_repository, sample_project_with_id):
        """Lister les projets avec pagination."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_all.return_value = [sample_project_with_id]

        # Act
        result = service.list_projects(offset=0, limit=20)

        # Assert
        mock_repository.find_all.assert_called_once_with(offset=0, limit=20)
        assert len(result) == 1
        assert result[0].id == 1


class TestDupliquerProjet:
    """Tests du cas d'usage dupliquer_projet."""

    def test_dupliquer_projet_success(self, mock_repository, sample_project_with_id):
        """Dupliquer un projet avec succès."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id
        mock_repository.exists_by_numero.return_value = False
        mock_repository.exists_by_name.return_value = False

        nouveau_projet = Project(
            id=2,
            numero="PROJ-002",
            nom="Duplicated Project",
            description=sample_project_with_id.description,
            date_debut=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            type=sample_project_with_id.type,
            stade=sample_project_with_id.stade,
            commentaire=sample_project_with_id.commentaire,
            heures_planifiees=sample_project_with_id.heures_planifiees,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=sample_project_with_id.responsable_id,
            entreprise_id=sample_project_with_id.entreprise_id,
            contact_id=sample_project_with_id.contact_id,
            date_creation=datetime.now()
        )
        mock_repository.save.return_value = nouveau_projet

        # Act
        result = service.dupliquer_projet(
            project_id=1,
            nouveau_numero="PROJ-002",
            nouveau_nom="Duplicated Project",
            nouvelle_date_debut=date.today(),
            nouvelle_date_echeance=date.today() + timedelta(days=30)
        )

        # Assert
        mock_repository.save.assert_called_once()
        assert result.id == 2
        assert result.numero == "PROJ-002"
        assert result.heures_reelles == 0.0


class TestSauvegarderCommeTemplate:
    """Tests du cas d'usage sauvegarder_comme_template."""

    def test_sauvegarder_comme_template_success(self, mock_repository, sample_project_with_id):
        """Sauvegarder un projet comme template."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id

        template_project = Project(
            id=sample_project_with_id.id,
            numero=sample_project_with_id.numero,
            nom=sample_project_with_id.nom,
            description=sample_project_with_id.description,
            date_debut=sample_project_with_id.date_debut,
            date_echeance=sample_project_with_id.date_echeance,
            type=sample_project_with_id.type,
            stade=sample_project_with_id.stade,
            commentaire=sample_project_with_id.commentaire,
            heures_planifiees=sample_project_with_id.heures_planifiees,
            heures_reelles=sample_project_with_id.heures_reelles,
            est_template=True,
            projet_template_id=sample_project_with_id.projet_template_id,
            responsable_id=sample_project_with_id.responsable_id,
            entreprise_id=sample_project_with_id.entreprise_id,
            contact_id=sample_project_with_id.contact_id,
            date_creation=sample_project_with_id.date_creation
        )
        mock_repository.update.return_value = template_project

        # Act
        result = service.sauvegarder_comme_template(1)

        # Assert
        mock_repository.update.assert_called_once()
        assert result.est_template is True


class TestCreerDepuisTemplate:
    """Tests du cas d'usage creer_depuis_template."""

    def test_creer_depuis_template_success(self, mock_repository):
        """Créer un projet depuis un template."""
        # Arrange
        service = ProjectService(mock_repository)

        # Template project
        template = Project(
            id=1,
            numero="TEMPLATE-001",
            nom="Template Project",
            description="A template",
            date_debut=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="Template",
            commentaire="Template comment",
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=True,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        mock_repository.find_by_id.return_value = template
        mock_repository.exists_by_numero.return_value = False
        mock_repository.exists_by_name.return_value = False

        new_project = Project(
            id=2,
            numero="PROJ-003",
            nom="New Project from Template",
            description=template.description,
            date_debut=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            type=template.type,
            stade=template.stade,
            commentaire=template.commentaire,
            heures_planifiees=template.heures_planifiees,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=1,
            responsable_id=2,
            entreprise_id=2,
            contact_id=None,
            date_creation=datetime.now()
        )
        mock_repository.save.return_value = new_project

        # Act
        result = service.creer_depuis_template(
            template_id=1,
            numero="PROJ-003",
            nom="New Project from Template",
            date_debut=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            responsable_id=2,
            entreprise_id=2
        )

        # Assert
        mock_repository.save.assert_called_once()
        assert result.projet_template_id == 1
        assert result.est_template is False

    def test_creer_depuis_template_non_template_fails(self, mock_repository, sample_project_with_id):
        """Erreur si le projet source n'est pas un template."""
        # Arrange
        service = ProjectService(mock_repository)
        mock_repository.find_by_id.return_value = sample_project_with_id

        # Act & Assert
        with pytest.raises(ValueError, match="n'est pas un template"):
            service.creer_depuis_template(
                template_id=1,
                numero="PROJ-004",
                nom="Should Fail",
                date_debut=date.today(),
                date_echeance=date.today() + timedelta(days=30),
                responsable_id=1,
                entreprise_id=1
            )


class TestCalculerAvancement:
    """Tests du cas d'usage calculer_avancement."""

    def test_calculer_avancement_success(self, mock_repository, sample_project_with_id):
        """Calculer l'avancement d'un projet."""
        # Arrange
        service = ProjectService(mock_repository)
        sample_project_with_id.heures_reelles = 50.0
        mock_repository.find_by_id.return_value = sample_project_with_id

        # Act
        result = service.calculer_avancement(1)

        # Assert
        assert result == 50.0


class TestCalculerEcartTemps:
    """Tests du cas d'usage calculer_ecart_temps."""

    def test_calculer_ecart_temps_success(self, mock_repository, sample_project_with_id):
        """Calculer l'écart temps d'un projet."""
        # Arrange
        service = ProjectService(mock_repository)
        sample_project_with_id.heures_reelles = 120.0
        mock_repository.find_by_id.return_value = sample_project_with_id

        # Act
        result = service.calculer_ecart_temps(1)

        # Assert
        assert result["heures_planifiees"] == 100.0
        assert result["heures_reelles"] == 120.0
        assert result["ecart"] == 20.0
        assert result["ecart_pourcentage"] == 20.0
