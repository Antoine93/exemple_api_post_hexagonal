"""
Service métier pour Utilisateur.

Ce service contient la logique métier complexe et orchestre
les interactions entre entités et repositories.
"""
from datetime import datetime
from typing import List

from src.domain.entities.user import Utilisateur, RoleUtilisateur
from src.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    DomainValidationError
)
from src.ports.primary.user_use_cases import UserUseCasesPort
from src.ports.secondary.user_repository import UserRepositoryPort


class UserService(UserUseCasesPort):
    """
    Service métier pour Utilisateur.

    Implémente UserUseCasesPort (port primaire).
    Dépend de UserRepositoryPort (port secondaire - interface uniquement).
    """

    def __init__(self, user_repository: UserRepositoryPort) -> None:
        """
        Injection de dépendance via le constructeur.

        Args:
            user_repository: Interface du repository (pas l'implémentation concrète)
        """
        self._repository = user_repository

    def creer_utilisateur(
        self,
        nom: str,
        prenom: str,
        email: str,
        mot_de_passe: str,
        role: RoleUtilisateur
    ) -> Utilisateur:
        """
        Cas d'usage: Créer un nouvel utilisateur.

        Logique métier:
        1. Vérifier l'unicité de l'email (règle métier)
        2. Hasher le mot de passe (sécurité)
        3. Créer l'entité (validation automatique)
        4. Sauvegarder via le repository

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
        # Règle métier: vérifier l'unicité de l'email
        if self._repository.exists_by_email(email):
            raise EntityAlreadyExistsError(f"Un utilisateur avec l'email {email} existe déjà")

        # Hasher le mot de passe
        try:
            mot_de_passe_hash = Utilisateur.hash_mot_de_passe(mot_de_passe)
        except ValueError as e:
            raise DomainValidationError(str(e))

        # Créer l'entité (validation automatique dans __post_init__)
        try:
            utilisateur = Utilisateur(
                id=None,
                nom=nom.strip(),
                prenom=prenom.strip(),
                email=email.strip().lower(),
                mot_de_passe_hash=mot_de_passe_hash,
                role=role,
                date_creation=datetime.now(),
                actif=True  # Par défaut, un utilisateur est actif
            )
        except ValueError as e:
            raise DomainValidationError(str(e))

        # Persistance via le port secondaire
        utilisateur_sauvegarde = self._repository.save(utilisateur)

        return utilisateur_sauvegarde

    def obtenir_utilisateur(self, user_id: int) -> Utilisateur:
        """
        Cas d'usage: Récupérer un utilisateur par son ID.

        Args:
            user_id: L'identifiant de l'utilisateur

        Returns:
            L'utilisateur trouvé

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        utilisateur = self._repository.find_by_id(user_id)

        if utilisateur is None:
            raise EntityNotFoundError(f"Utilisateur avec ID {user_id} introuvable")

        return utilisateur

    def lister_utilisateurs(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[Utilisateur]:
        """
        Cas d'usage: Lister les utilisateurs avec pagination.

        Args:
            offset: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs

        Raises:
            DomainValidationError: Si les paramètres de pagination sont invalides
        """
        # Validation des paramètres
        if offset < 0:
            raise DomainValidationError("L'offset ne peut pas être négatif")

        if limit < 1 or limit > 100:
            raise DomainValidationError("Le limit doit être entre 1 et 100")

        return self._repository.find_all(offset=offset, limit=limit)

    def modifier_utilisateur(
        self,
        user_id: int,
        nom: str = None,
        prenom: str = None,
        email: str = None
    ) -> Utilisateur:
        """
        Cas d'usage: Modifier les informations d'un utilisateur.

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
        # Récupérer l'utilisateur existant
        utilisateur = self.obtenir_utilisateur(user_id)

        # Appliquer les modifications (seulement les champs fournis)
        if nom is not None:
            utilisateur.nom = nom.strip()

        if prenom is not None:
            utilisateur.prenom = prenom.strip()

        if email is not None:
            email_normalise = email.strip().lower()
            # Vérifier l'unicité si l'email change
            if email_normalise != utilisateur.email:
                if self._repository.exists_by_email(email_normalise):
                    raise EntityAlreadyExistsError(
                        f"Un utilisateur avec l'email {email_normalise} existe déjà"
                    )
                utilisateur.email = email_normalise

        # Re-valider l'entité après modification
        try:
            utilisateur._validate()
        except ValueError as e:
            raise DomainValidationError(str(e))

        # Sauvegarder les modifications
        utilisateur_mis_a_jour = self._repository.update(utilisateur)

        return utilisateur_mis_a_jour

    def supprimer_utilisateur(self, user_id: int) -> bool:
        """
        Cas d'usage: Supprimer un utilisateur (soft delete - désactivation).

        Règle métier: Un utilisateur n'est jamais vraiment supprimé,
        il est désactivé pour conserver l'historique.

        Args:
            user_id: L'identifiant de l'utilisateur à supprimer

        Returns:
            True si la suppression a réussi

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        # Récupérer l'utilisateur
        utilisateur = self.obtenir_utilisateur(user_id)

        # Soft delete: désactiver l'utilisateur
        utilisateur.desactiver()

        # Sauvegarder la modification
        self._repository.update(utilisateur)

        return True

    def activer_desactiver_utilisateur(
        self,
        user_id: int,
        actif: bool
    ) -> Utilisateur:
        """
        Cas d'usage: Active ou désactive un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            actif: True pour activer, False pour désactiver

        Returns:
            L'utilisateur modifié

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
        """
        # Récupérer l'utilisateur
        utilisateur = self.obtenir_utilisateur(user_id)

        # Appliquer le changement de statut
        if actif:
            utilisateur.activer()
        else:
            utilisateur.desactiver()

        # Sauvegarder
        utilisateur_mis_a_jour = self._repository.update(utilisateur)

        return utilisateur_mis_a_jour

    def changer_role(
        self,
        user_id: int,
        nouveau_role: RoleUtilisateur
    ) -> Utilisateur:
        """
        Cas d'usage: Change le rôle d'un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            nouveau_role: Le nouveau rôle à attribuer

        Returns:
            L'utilisateur avec son nouveau rôle

        Raises:
            EntityNotFoundError: Si l'utilisateur n'existe pas
            DomainValidationError: Si le changement de rôle n'est pas autorisé
        """
        # Récupérer l'utilisateur
        utilisateur = self.obtenir_utilisateur(user_id)

        # Appliquer le changement de rôle (validation dans l'entité)
        try:
            utilisateur.changer_role(nouveau_role)
        except ValueError as e:
            raise DomainValidationError(str(e))

        # Sauvegarder
        utilisateur_mis_a_jour = self._repository.update(utilisateur)

        return utilisateur_mis_a_jour

    def changer_mot_de_passe(
        self,
        user_id: int,
        ancien_mot_de_passe: str,
        nouveau_mot_de_passe: str
    ) -> bool:
        """
        Cas d'usage: Change le mot de passe d'un utilisateur.

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
        # Récupérer l'utilisateur
        utilisateur = self.obtenir_utilisateur(user_id)

        # Vérifier l'ancien mot de passe (règle de sécurité)
        if not utilisateur.verifier_mot_de_passe(ancien_mot_de_passe):
            raise DomainValidationError("L'ancien mot de passe est incorrect")

        # Hasher le nouveau mot de passe
        try:
            nouveau_hash = Utilisateur.hash_mot_de_passe(nouveau_mot_de_passe)
        except ValueError as e:
            raise DomainValidationError(str(e))

        # Mettre à jour le hash
        utilisateur.mot_de_passe_hash = nouveau_hash

        # Sauvegarder
        self._repository.update(utilisateur)

        return True
