"""
Port primaire: interface des cas d'usage pour Utilisateur.

Ce port définit le CONTRAT que le domaine expose vers l'extérieur.
Les adapters primaires (API, CLI) dépendent de cette interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.user import Utilisateur, RoleUtilisateur


class UserUseCasesPort(ABC):
    """
    Interface des cas d'usage pour Utilisateur.

    Cette interface définit les opérations métier que le domaine
    expose aux adapters primaires.
    """

    @abstractmethod
    def creer_utilisateur(
        self,
        nom: str,
        prenom: str,
        email: str,
        mot_de_passe: str,
        role: RoleUtilisateur
    ) -> Utilisateur:
        """
        Crée un nouvel utilisateur.

        Args:
            nom: Nom de famille de l'utilisateur
            prenom: Prénom de l'utilisateur
            email: Adresse email (doit être unique)
            mot_de_passe: Mot de passe en clair (sera hashé)
            role: Rôle de l'utilisateur

        Returns:
            L'utilisateur créé avec son ID

        Raises:
            EntityAlreadyExistsError: Si un utilisateur avec cet email existe déjà
            DomainValidationError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def obtenir_utilisateur(self, user_id: int) -> Utilisateur:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: L'identifiant de l'utilisateur

        Returns:
            L'utilisateur trouvé

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        pass

    @abstractmethod
    def lister_utilisateurs(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[Utilisateur]:
        """
        Liste les utilisateurs avec pagination.

        Args:
            offset: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs
        """
        pass

    @abstractmethod
    def modifier_utilisateur(
        self,
        user_id: int,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        email: Optional[str] = None
    ) -> Utilisateur:
        """
        Modifie les informations d'un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            nom: Nouveau nom (optionnel)
            prenom: Nouveau prénom (optionnel)
            email: Nouvel email (optionnel)

        Returns:
            L'utilisateur modifié

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
            EntityAlreadyExistsError: Si l'email existe déjà
            DomainValidationError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def supprimer_utilisateur(self, user_id: int) -> bool:
        """
        Supprime un utilisateur (soft delete - désactivation).

        Args:
            user_id: L'identifiant de l'utilisateur à supprimer

        Returns:
            True si la suppression a réussi, False sinon

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        pass

    @abstractmethod
    def activer_desactiver_utilisateur(
        self,
        user_id: int,
        actif: bool
    ) -> Utilisateur:
        """
        Active ou désactive un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            actif: True pour activer, False pour désactiver

        Returns:
            L'utilisateur modifié

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        pass

    @abstractmethod
    def changer_role(
        self,
        user_id: int,
        nouveau_role: RoleUtilisateur
    ) -> Utilisateur:
        """
        Change le rôle d'un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            nouveau_role: Le nouveau rôle à attribuer

        Returns:
            L'utilisateur avec son nouveau rôle

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
            DomainValidationError: Si le changement de rôle n'est pas autorisé
        """
        pass

    @abstractmethod
    def changer_mot_de_passe(
        self,
        user_id: int,
        ancien_mot_de_passe: str,
        nouveau_mot_de_passe: str
    ) -> bool:
        """
        Change le mot de passe d'un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            ancien_mot_de_passe: L'ancien mot de passe (pour vérification)
            nouveau_mot_de_passe: Le nouveau mot de passe

        Returns:
            True si le changement a réussi

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
            DomainValidationError: Si l'ancien mot de passe est incorrect
        """
        pass
