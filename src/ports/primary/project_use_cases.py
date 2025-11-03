"""
Port primaire: interface des cas d'usage.
Définit le CONTRAT que le domaine expose vers l'extérieur.
Les adapters primaires dépendent de CETTE INTERFACE.
"""
from abc import ABC, abstractmethod
from domain.entities.project import Project


class ProjectUseCasesPort(ABC):
    """
    Interface des cas d'usage pour les projets.

    Cette interface définit les opérations métier que le domaine
    expose aux adapters primaires (API, CLI, etc.).
    """

    @abstractmethod
    def create_project(
        self,
        name: str,
        description: str,
        start_date,
        end_date,
        budget: float,
        comment: str,
        manager_id: int
    ) -> Project:
        """Crée un nouveau projet."""
        pass

    @abstractmethod
    def get_project(self, project_id: int) -> Project:
        """Récupère un projet par son ID."""
        pass
