"""
Tests unitaires pour l'énumération ProjectType.
"""
import pytest
from src.domain.entities.project_type import ProjectType


class TestProjectType:
    """Tests pour l'enum ProjectType."""

    def test_enum_has_all_values(self):
        """L'enum doit avoir toutes les valeurs définies."""
        assert hasattr(ProjectType, "INTERNAL")
        assert hasattr(ProjectType, "EXTERNAL")
        assert hasattr(ProjectType, "MAINTENANCE")
        assert hasattr(ProjectType, "DEVELOPMENT")

    def test_enum_values_are_correct(self):
        """Les valeurs de l'enum doivent correspondre aux spécifications."""
        assert ProjectType.INTERNAL.value == "INTERNAL"
        assert ProjectType.EXTERNAL.value == "EXTERNAL"
        assert ProjectType.MAINTENANCE.value == "MAINTENANCE"
        assert ProjectType.DEVELOPMENT.value == "DEVELOPMENT"

    def test_enum_is_string_based(self):
        """L'enum doit hériter de str pour la sérialisation."""
        assert isinstance(ProjectType.INTERNAL, str)
        assert isinstance(ProjectType.EXTERNAL, str)
        assert isinstance(ProjectType.MAINTENANCE, str)
        assert isinstance(ProjectType.DEVELOPMENT, str)

    def test_enum_str_representation(self):
        """La représentation string doit retourner la valeur."""
        assert str(ProjectType.INTERNAL) == "INTERNAL"
        assert str(ProjectType.EXTERNAL) == "EXTERNAL"
        assert str(ProjectType.MAINTENANCE) == "MAINTENANCE"
        assert str(ProjectType.DEVELOPMENT) == "DEVELOPMENT"

    def test_enum_comparison(self):
        """Les valeurs de l'enum doivent être comparables."""
        assert ProjectType.INTERNAL == ProjectType.INTERNAL
        assert ProjectType.INTERNAL != ProjectType.EXTERNAL
        assert ProjectType.MAINTENANCE == ProjectType.MAINTENANCE

    def test_enum_can_be_created_from_string(self):
        """On doit pouvoir créer un enum depuis une string."""
        assert ProjectType("INTERNAL") == ProjectType.INTERNAL
        assert ProjectType("EXTERNAL") == ProjectType.EXTERNAL
        assert ProjectType("MAINTENANCE") == ProjectType.MAINTENANCE
        assert ProjectType("DEVELOPMENT") == ProjectType.DEVELOPMENT

    def test_invalid_value_raises_error(self):
        """Une valeur invalide doit lever une erreur."""
        with pytest.raises(ValueError):
            ProjectType("INVALIDE")

    def test_enum_iteration(self):
        """On doit pouvoir itérer sur les valeurs de l'enum."""
        values = list(ProjectType)
        assert len(values) == 4
        assert ProjectType.INTERNAL in values
        assert ProjectType.EXTERNAL in values
        assert ProjectType.MAINTENANCE in values
        assert ProjectType.DEVELOPMENT in values
