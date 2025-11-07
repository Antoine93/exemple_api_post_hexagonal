"""
Port primaire: interface des cas d'usage.
Définit le CONTRAT que le domaine expose vers l'extérieur.
Les adapters primaires dépendent de CETTE INTERFACE.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from src.domain.entities.project import Project


class ProjectUseCasesPort(ABC):
    """
    Interface des cas d'usage pour les projets.

    Cette interface définit les opérations métier que le domaine
    expose aux adapters primaires (API, CLI, etc.).

    Type Safety:
    - Toutes les méthodes ont des annotations de type complètes
    - Utilise Optional pour les paramètres optionnels
    - Utilise datetime.date pour les dates (pas de types ambigus)
    """

    @abstractmethod
    def create_project(
        self,
        name: str,
        description: str,
        start_date: date,
        end_date: date,
        budget: float,
        comment: Optional[str],
        manager_id: int
    ) -> Project:
        """
        Crée un nouveau projet.

        Args:
            name: Nom du projet (unique)
            description: Description détaillée
            start_date: Date de début du projet
            end_date: Date de fin du projet (doit être après start_date)
            budget: Budget alloué (doit être positif)
            comment: Commentaire optionnel
            manager_id: ID du manager responsable

        Returns:
            Le projet créé avec son ID généré

        Raises:
            ValueError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def get_project(self, project_id: int) -> Project:
        """
        Récupère un projet par son ID.

        Args:
            project_id: L'identifiant unique du projet

        Returns:
            Le projet trouvé

        Raises:
            ValueError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        budget: Optional[float] = None,
        comment: Optional[str] = None,
        manager_id: Optional[int] = None
    ) -> Project:
        """
        Met à jour un projet existant.

        Args:
            project_id: L'identifiant du projet à modifier
            name: Nouveau nom (optionnel)
            description: Nouvelle description (optionnel)
            start_date: Nouvelle date de début (optionnel)
            end_date: Nouvelle date de fin (optionnel)
            budget: Nouveau budget (optionnel)
            comment: Nouveau commentaire (optionnel)
            manager_id: Nouvel ID du manager (optionnel)

        Returns:
            Le projet modifié

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
            ProjectAlreadyExistsError: Si le nouveau nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def delete_project(self, project_id: int) -> bool:
        """
        Supprime un projet.

        Args:
            project_id: L'identifiant du projet à supprimer

        Returns:
            True si le projet a été supprimé, False si le projet n'existait pas

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def list_projects(self, offset: int = 0, limit: int = 20) -> list[Project]:
        """
        Liste les projets avec pagination.

        Args:
            offset: Nombre de projets à ignorer (pour la pagination)
            limit: Nombre maximum de projets à retourner

        Returns:
            Liste de projets (peut être vide)
        """
        pass
