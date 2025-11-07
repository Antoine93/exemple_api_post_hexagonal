"""
Unit tests for Project entity.

Tests the business logic and validation rules in the Project entity.
No infrastructure dependencies - pure domain logic testing.
"""
import pytest
from datetime import date, timedelta

from src.domain.entities.project import Project


class TestProjectValidation:
    """Test suite for Project validation rules."""

    def test_project_creation_valid(self):
        """Test that a valid project can be created successfully."""
        # Arrange
        today = date.today()

        # Act
        project = Project(
            id=None,
            name="Test Project",
            description="A test project",
            start_date=today,
            end_date=today + timedelta(days=30),
            budget=10000.0,
            comment="Test comment",
            manager_id=1
        )

        # Assert
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.start_date == today
        assert project.end_date == today + timedelta(days=30)
        assert project.budget == 10000.0
        assert project.comment == "Test comment"
        assert project.manager_id == 1

    def test_project_rejects_empty_name(self):
        """Test that project creation fails with empty name."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le nom du projet ne peut pas être vide"):
            Project(
                id=None,
                name="",
                description="Test",
                start_date=today,
                end_date=today + timedelta(days=30),
                budget=10000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_whitespace_only_name(self):
        """Test that project creation fails with whitespace-only name."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le nom du projet ne peut pas être vide"):
            Project(
                id=None,
                name="   ",
                description="Test",
                start_date=today,
                end_date=today + timedelta(days=30),
                budget=10000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_negative_budget(self):
        """Test that project creation fails with negative budget."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le budget doit être positif"):
            Project(
                id=None,
                name="Test Project",
                description="Test",
                start_date=today,
                end_date=today + timedelta(days=30),
                budget=-1000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_zero_budget(self):
        """Test that project creation fails with zero budget."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="Le budget doit être positif"):
            Project(
                id=None,
                name="Test Project",
                description="Test",
                start_date=today,
                end_date=today + timedelta(days=30),
                budget=0.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_end_date_before_start_date(self):
        """Test that project creation fails when end_date is before start_date."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="La date de fin doit être après la date de début"):
            Project(
                id=None,
                name="Test Project",
                description="Test",
                start_date=today,
                end_date=today - timedelta(days=1),
                budget=10000.0,
                comment=None,
                manager_id=1
            )

    def test_project_rejects_equal_dates(self):
        """Test that project creation fails when start_date equals end_date."""
        # Arrange
        today = date.today()

        # Act & Assert
        with pytest.raises(ValueError, match="La date de fin doit être après la date de début"):
            Project(
                id=None,
                name="Test Project",
                description="Test",
                start_date=today,
                end_date=today,
                budget=10000.0,
                comment=None,
                manager_id=1
            )


class TestProjectBusinessLogic:
    """Test suite for Project business logic methods."""

    def test_project_is_active_when_in_date_range(self):
        """Test that a project is active when current date is within range."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            name="Active Project",
            description="Currently active",
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10),
            budget=10000.0,
            comment=None,
            manager_id=1
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
            name="Future Project",
            description="Not started yet",
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=30),
            budget=10000.0,
            comment=None,
            manager_id=1
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
            name="Past Project",
            description="Already finished",
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
            budget=10000.0,
            comment=None,
            manager_id=1
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
            name="Active Project",
            description="Has days remaining",
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=15),
            budget=10000.0,
            comment=None,
            manager_id=1
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
            name="Past Project",
            description="No days remaining",
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=5),
            budget=10000.0,
            comment=None,
            manager_id=1
        )

        # Act
        result = project.days_remaining()

        # Assert
        assert result == 0

    def test_days_remaining_on_last_day(self):
        """Test that days_remaining is 0 when today equals end_date."""
        # Arrange
        today = date.today()
        project = Project(
            id=1,
            name="Ending Project",
            description="Last day today",
            start_date=today - timedelta(days=30),
            end_date=today,
            budget=10000.0,
            comment=None,
            manager_id=1
        )

        # Act
        result = project.days_remaining()

        # Assert
        assert result == 0
