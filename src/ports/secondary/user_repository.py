"""
Port secondaire: interface du repository pour Utilisateur.

Ce port définit le CONTRAT de persistance que le domaine attend.
Le domaine dépend de cette INTERFACE, pas de l'implémentation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import Utilisateur


class UserRepositoryPort(ABC):
    """
    Interface du repository pour Utilisateur.

    Cette interface définit les opérations de persistance nécessaires
    pour le domaine, sans se soucier de l'implémentation technique.
    """

    @abstractmethod
    def save(self, user: Utilisateur) -> Utilisateur:
        """
        Sauvegarde un utilisateur et retourne l'utilisateur avec son ID.

        Args:
            user: L'utilisateur à sauvegarder

        Returns:
            L'utilisateur sauvegardé avec son ID généré

        Raises:
            RepositoryError: Si la sauvegarde échoue
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[Utilisateur]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: L'identifiant de l'utilisateur

        Returns:
            L'utilisateur trouvé ou None
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Utilisateur]:
        """
        Récupère un utilisateur par son email.

        Args:
            email: L'adresse email de l'utilisateur

        Returns:
            L'utilisateur trouvé ou None
        """
        pass

    @abstractmethod
    def find_all(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[Utilisateur]:
        """
        Récupère tous les utilisateurs avec pagination.

        Args:
            offset: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Vérifie si un utilisateur avec cet email existe.

        Args:
            email: L'adresse email à vérifier

        Returns:
            True si l'utilisateur existe, False sinon
        """
        pass

    @abstractmethod
    def update(self, user: Utilisateur) -> Utilisateur:
        """
        Met à jour un utilisateur existant.

        Args:
            user: L'utilisateur avec les nouvelles valeurs

        Returns:
            L'utilisateur mis à jour

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Supprime un utilisateur (ou le désactive selon la logique métier).

        Args:
            user_id: L'identifiant de l'utilisateur à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        pass
