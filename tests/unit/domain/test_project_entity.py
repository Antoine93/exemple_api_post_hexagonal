"""
Unit tests for Project entity.

Tests the business logic and validation rules in the Project entity.
No infrastructure dependencies - pure domain logic testing.
"""
import pytest
from datetime import date, datetime, timedelta

from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType


class TestProjectValidation:
    """Test suite for Project validation rules."""

    def test_project_creation_valid(self):
        """Test that a valid project can be created successfully."""
        # Arrange
        today = date.today()
        now = datetime.now()

        # Act
        project = Project(
            id=None,
            numero="PROJ-001",
            nom="Test Project",
            description="A test project",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire="Test comment",
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=now
        )

        # Assert
        assert project.numero == "PROJ-001"
        assert project.nom == "Test Project"
        assert project.description == "A test project"
        assert project.date_debut == today
        assert project.date_echeance == today + timedelta(days=30)
        assert project.type == ProjectType.INTERNAL
        assert project.stade == "En cours"
        assert project.commentaire == "Test comment"
        assert project.heures_planifiees == 100.0
        assert project.heures_reelles == 0.0
        assert project.est_template is False
        assert project.projet_template_id is None
        assert project.responsable_id == 1
        assert project.entreprise_id == 1
        assert project.contact_id is None

    def test_project_rejects_empty_nom(self):
        """Test that project creation fails with empty nom."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le nom du projet ne peut pas être vide"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_whitespace_only_nom(self):
        """Test that project creation fails with whitespace-only nom."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le nom du projet ne peut pas être vide"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="   ",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_empty_numero(self):
        """Test that project creation fails with empty numero."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le numéro du projet ne peut pas être vide"):
            Project(
                id=None,
                numero="",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_negative_heures_planifiees(self):
        """Test that project creation fails with negative heures_planifiees."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Les heures planifiées doivent être >= 0"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=-10.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_negative_heures_reelles(self):
        """Test that project creation fails with negative heures_reelles."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Les heures réelles doivent être >= 0"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=-5.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_end_date_before_start_date(self):
        """Test that project creation fails when date_echeance is before date_debut."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="La date d'échéance doit être après la date de début"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today - timedelta(days=1),
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_equal_dates(self):
        """Test that project creation fails when date_debut equals date_echeance."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="La date d'échéance doit être après la date de début"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today,
                type=ProjectType.INTERNAL,
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )

    def test_project_rejects_invalid_type(self):
        """Test that project creation fails with invalid type."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le type doit être une instance de ProjectType"):
            Project(
                id=None,
                numero="PROJ-001",
                nom="Test Project",
                description="Test",
                date_debut=today,
                date_echeance=today + timedelta(days=30),
                type="INVALIDE",  # type: ignore
                stade=None,
                commentaire=None,
                heures_planifiees=100.0,
                heures_reelles=0.0,
                est_template=False,
                projet_template_id=None,
                responsable_id=1,
                entreprise_id=1,
                contact_id=None,
                date_creation=datetime.now()
            )


class TestProjectBusinessLogic:
    """Test suite for Project business logic methods."""

    def test_project_is_active_when_in_date_range(self):
        """Test that a project is active when current date is within range."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-001",
            nom="Active Project",
            description="Currently active",
            date_debut=today - timedelta(days=10),
            date_echeance=today + timedelta(days=10),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=50.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.is_active()

        # Assert
        assert result is True

    def test_project_is_not_active_before_start_date(self):
        """Test that a project is not active before its start date."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-002",
            nom="Future Project",
            description="Not started yet",
            date_debut=today + timedelta(days=10),
            date_echeance=today + timedelta(days=30),
            type=ProjectType.EXTERNAL,
            stade="Planifié",
            commentaire=None,
            heures_planifiees=200.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.is_active()

        # Assert
        assert result is False

    def test_project_is_not_active_after_end_date(self):
        """Test that a project is not active after its end date."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-003",
            nom="Past Project",
            description="Already finished",
            date_debut=today - timedelta(days=30),
            date_echeance=today - timedelta(days=1),
            type=ProjectType.MAINTENANCE,
            stade="Terminé",
            commentaire=None,
            heures_planifiees=150.0,
            heures_reelles=150.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.is_active()

        # Assert
        assert result is False

    def test_days_remaining_positive(self):
        """Test that days_remaining returns correct positive value."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-004",
            nom="Active Project",
            description="Has days remaining",
            date_debut=today - timedelta(days=10),
            date_echeance=today + timedelta(days=15),
            type=ProjectType.DEVELOPMENT,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=30.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.days_remaining()

        # Assert
        assert result == 15

    def test_days_remaining_zero_after_end(self):
        """Test that days_remaining returns 0 for past projects."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-005",
            nom="Past Project",
            description="No days remaining",
            date_debut=today - timedelta(days=30),
            date_echeance=today - timedelta(days=5),
            type=ProjectType.INTERNAL,
            stade="Terminé",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=105.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.days_remaining()

        # Assert
        assert result == 0

    def test_calculer_avancement_normal(self):
        """Test avancement calculation with normal values."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-006",
            nom="Test Project",
            description="Test avancement",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=50.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.calculer_avancement()

        # Assert
        assert result == 50.0

    def test_calculer_avancement_over_100_percent(self):
        """Test that avancement is capped at 100%."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-007",
            nom="Test Project",
            description="Over budget",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.EXTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=150.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.calculer_avancement()

        # Assert
        assert result == 100.0

    def test_calculer_avancement_zero_heures_planifiees(self):
        """Test avancement with zero heures_planifiees."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-008",
            nom="Test Project",
            description="No planned hours",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.MAINTENANCE,
            stade="En cours",
            commentaire=None,
            heures_planifiees=0.0,
            heures_reelles=10.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.calculer_avancement()

        # Assert
        assert result == 0.0

    def test_calculer_ecart_temps_positive(self):
        """Test écart temps with positive value (over budget)."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-009",
            nom="Test Project",
            description="Over budget",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.DEVELOPMENT,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=120.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.calculer_ecart_temps()

        # Assert
        assert result == 20.0

    def test_calculer_ecart_temps_negative(self):
        """Test écart temps with negative value (under budget)."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-010",
            nom="Test Project",
            description="Under budget",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=75.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.calculer_ecart_temps()

        # Assert
        assert result == -25.0

    def test_est_en_retard_hours_exceeded(self):
        """Test that project is late when hours exceeded."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-011",
            nom="Test Project",
            description="Hours exceeded",
            date_debut=today - timedelta(days=10),
            date_echeance=today + timedelta(days=10),
            type=ProjectType.EXTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=110.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.est_en_retard()

        # Assert
        assert result is True

    def test_est_en_retard_date_exceeded(self):
        """Test that project is late when date exceeded."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-012",
            nom="Test Project",
            description="Date exceeded",
            date_debut=today - timedelta(days=30),
            date_echeance=today - timedelta(days=1),
            type=ProjectType.MAINTENANCE,
            stade="En retard",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=90.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.est_en_retard()

        # Assert
        assert result is True

    def test_est_en_retard_false(self):
        """Test that project is not late when on track."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-013",
            nom="Test Project",
            description="On track",
            date_debut=today - timedelta(days=10),
            date_echeance=today + timedelta(days=10),
            type=ProjectType.DEVELOPMENT,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=50.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.est_en_retard()

        # Assert
        assert result is False

    def test_is_template_true(self):
        """Test is_template when est_template is True."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="TEMPLATE-001",
            nom="Template Project",
            description="This is a template",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="Template",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=True,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.is_template()

        # Assert
        assert result is True

    def test_is_template_false(self):
        """Test is_template when est_template is False."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-014",
            nom="Regular Project",
            description="Not a template",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.EXTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.is_template()

        # Assert
        assert result is False

    def test_created_from_template_true(self):
        """Test created_from_template when projet_template_id is set."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-015",
            nom="Project from Template",
            description="Created from template",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.DEVELOPMENT,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=10,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.created_from_template()

        # Assert
        assert result is True

    def test_created_from_template_false(self):
        """Test created_from_template when projet_template_id is None."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            numero="PROJ-016",
            nom="Regular Project",
            description="Not from template",
            date_debut=today,
            date_echeance=today + timedelta(days=30),
            type=ProjectType.INTERNAL,
            stade="En cours",
            commentaire=None,
            heures_planifiees=100.0,
            heures_reelles=0.0,
            est_template=False,
            projet_template_id=None,
            responsable_id=1,
            entreprise_id=1,
            contact_id=None,
            date_creation=datetime.now()
        )

        # Act
        result = project.created_from_template()

        # Assert
        assert result is False
