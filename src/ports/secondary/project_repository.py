"""
Port secondaire: interface du repository.
Définit le CONTRAT que doit respecter n'importe quelle implémentation de stockage.
Le domaine dépend de CETTE INTERFACE, pas de l'implémentation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.project import Project


class ProjectRepositoryPort(ABC):
    """
    Interface (Protocol) du repository de projets.

    Cette interface définit les opérations de persistance nécessaires
    pour le domaine, sans se soucier de l'implémentation technique.
    """

    @abstractmethod
    def save(self, project: Project) -> Project:
        """
        Sauvegarde un projet et retourne le projet avec son ID.

        Args:
            project: L'entité Project à sauvegarder

        Returns:
            Le projet sauvegardé avec son ID généré

        Raises:
            RepositoryError: Si la sauvegarde échoue
        """
        pass

    @abstractmethod
    def find_by_id(self, project_id: int) -> Optional[Project]:
        """
        Récupère un projet par son ID.

        Args:
            project_id: L'identifiant du projet

        Returns:
            Le projet trouvé ou None
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Project]:
        """
        Récupère tous les projets.

        Returns:
            Liste de tous les projets
        """
        pass

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Vérifie si un projet avec ce nom existe déjà.

        Args:
            name: Le nom du projet à vérifier

        Returns:
            True si le projet existe, False sinon
        """
        pass

    @abstractmethod
    def delete(self, project_id: int) -> bool:
        """
        Supprime un projet.

        Args:
            project_id: L'identifiant du projet à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        pass
