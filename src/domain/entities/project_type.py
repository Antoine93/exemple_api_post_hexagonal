"""
Énumération ProjectType - PURE PYTHON.

Définit les types de projets possibles selon la spécification métier.
"""
from enum import Enum


class ProjectType(str, Enum):
    """
    Types de projets disponibles dans le système.

    Hérite de str pour faciliter la sérialisation JSON et la compatibilité
    avec Pydantic et SQLAlchemy.

    Valeurs:
        INTERNAL: Projet interne à l'entreprise
        EXTERNAL: Projet pour un client externe
        MAINTENANCE: Projet de maintenance
        DEVELOPMENT: Projet de développement
    """

    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    MAINTENANCE = "MAINTENANCE"
    DEVELOPMENT = "DEVELOPMENT"

    def __str__(self) -> str:
        """Retourne la valeur string de l'enum."""
        return self.value
