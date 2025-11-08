"""
Port secondaire: interface du repository pour Project.

Ce port définit le CONTRAT de persistance que le domaine attend.
Le domaine dépend de cette INTERFACE, pas de l'implémentation.
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.project import Project


class ProjectRepositoryPort(ABC):
    """
    Interface du repository pour Project.

    Cette interface définit les opérations de persistance nécessaires
    pour le domaine, sans se soucier de l'implémentation technique
    (SQLAlchemy, MongoDB, fichiers, etc.).

    IMPORTANT: Le repository travaille UNIQUEMENT avec des entités du domaine,
    jamais avec des modèles ORM ou DTOs.
    """

    @abstractmethod
    def save(self, project: Project) -> Project:
        """
        Sauvegarde un projet et retourne le projet avec son ID.

        Args:
            project: Le projet à sauvegarder (ID peut être None)

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
            Le projet trouvé ou None si non trouvé
        """
        pass

    @abstractmethod
    def find_all(self, offset: int = 0, limit: int = 20) -> list[Project]:
        """
        Récupère tous les projets avec pagination.

        Args:
            offset: Nombre de projets à sauter
            limit: Nombre maximum de projets à retourner

        Returns:
            Liste des projets (peut être vide)
        """
        pass

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Vérifie si un projet avec ce nom existe.

        Args:
            name: Le nom à vérifier

        Returns:
            True si un projet avec ce nom existe, False sinon
        """
        pass

    @abstractmethod
    def exists_by_numero(self, numero: str) -> bool:
        """
        Vérifie si un projet avec ce numéro existe.

        Args:
            numero: Le numéro à vérifier

        Returns:
            True si un projet avec ce numéro existe, False sinon
        """
        pass

    @abstractmethod
    def delete(self, project_id: int) -> bool:
        """
        Supprime un projet.

        Args:
            project_id: L'identifiant du projet à supprimer

        Returns:
            True si la suppression a réussi, False si le projet n'existait pas

        Raises:
            RepositoryError: Si la suppression échoue
        """
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        """
        Met à jour un projet existant.

        Args:
            project: Le projet avec les nouvelles valeurs (ID requis)

        Returns:
            Le projet mis à jour

        Raises:
            RepositoryError: Si la mise à jour échoue
            ValueError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def find_templates(self) -> list[Project]:
        """
        Récupère tous les projets qui sont des templates.

        Returns:
            Liste des projets avec est_template=True
        """
        pass

    @abstractmethod
    def find_by_template_id(self, template_id: int) -> list[Project]:
        """
        Trouve tous les projets créés depuis un template spécifique.

        Args:
            template_id: L'ID du template source

        Returns:
            Liste des projets avec projet_template_id=template_id
        """
        pass

    @abstractmethod
    def find_by_entreprise(self, entreprise_id: int) -> list[Project]:
        """
        Trouve tous les projets d'une entreprise.

        Args:
            entreprise_id: L'ID de l'entreprise

        Returns:
            Liste des projets de cette entreprise
        """
        pass

    @abstractmethod
    def find_by_responsable(self, responsable_id: int) -> list[Project]:
        """
        Trouve tous les projets d'un responsable.

        Args:
            responsable_id: L'ID du responsable

        Returns:
            Liste des projets de ce responsable
        """
        pass
