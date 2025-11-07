"""
Entité Utilisateur du domaine.

Cette entité représente un utilisateur du système avec ses droits et permissions.

Règles métier:
- L'email doit être unique et valide
- Le nom et prénom ne peuvent pas être vides
- Le mot de passe doit être hashé en SHA-256
- Un utilisateur a un rôle (ADMINISTRATEUR, GESTIONNAIRE, EMPLOYE)
- Un utilisateur peut être actif ou inactif
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib
import re


class RoleUtilisateur(Enum):
    """Rôles possibles d'un utilisateur."""
    ADMINISTRATEUR = "ADMINISTRATEUR"
    GESTIONNAIRE = "GESTIONNAIRE"
    EMPLOYE = "EMPLOYE"


@dataclass
class Utilisateur:
    """
    Entité Utilisateur avec validation métier intégrée.

    Attributes:
        id: Identifiant unique (None si pas encore persisté)
        nom: Nom de famille de l'utilisateur
        prenom: Prénom de l'utilisateur
        email: Adresse email (unique)
        mot_de_passe_hash: Mot de passe hashé en SHA-256
        role: Rôle de l'utilisateur dans le système
        date_creation: Date de création du compte
        actif: Indique si le compte est actif
    """

    id: Optional[int]
    nom: str
    prenom: str
    email: str
    mot_de_passe_hash: str
    role: RoleUtilisateur
    date_creation: datetime
    actif: bool

    def __post_init__(self) -> None:
        """Validation automatique à la création."""
        self._validate()

    def _validate(self) -> None:
        """
        Valide les règles métier de l'entité.

        Raises:
            ValueError: Si une règle métier n'est pas respectée
        """
        if not self.nom or self.nom.strip() == "":
            raise ValueError("Le nom ne peut pas être vide")

        if not self.prenom or self.prenom.strip() == "":
            raise ValueError("Le prénom ne peut pas être vide")

        if not self.email or self.email.strip() == "":
            raise ValueError("L'email ne peut pas être vide")

        # Validation format email (simple)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("L'email n'est pas au format valide")

        if not self.mot_de_passe_hash or len(self.mot_de_passe_hash) != 64:
            raise ValueError("Le mot de passe doit être hashé en SHA-256 (64 caractères)")

    @staticmethod
    def hash_mot_de_passe(mot_de_passe_clair: str) -> str:
        """
        Hash un mot de passe en clair avec SHA-256.

        Args:
            mot_de_passe_clair: Le mot de passe en texte clair

        Returns:
            Le hash SHA-256 du mot de passe en hexadécimal

        Raises:
            ValueError: Si le mot de passe est vide ou trop court
        """
        if not mot_de_passe_clair or len(mot_de_passe_clair) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

        return hashlib.sha256(mot_de_passe_clair.encode('utf-8')).hexdigest()

    def verifier_mot_de_passe(self, mot_de_passe_clair: str) -> bool:
        """
        Vérifie si un mot de passe en clair correspond au hash stocké.

        Args:
            mot_de_passe_clair: Le mot de passe à vérifier

        Returns:
            True si le mot de passe correspond, False sinon
        """
        hash_a_verifier = self.hash_mot_de_passe(mot_de_passe_clair)
        return hash_a_verifier == self.mot_de_passe_hash

    def verifier_permission(self, action: str) -> bool:
        """
        Vérifie si l'utilisateur a la permission d'effectuer une action.

        Logique métier des permissions:
        - ADMINISTRATEUR: toutes les permissions
        - GESTIONNAIRE: gestion de projets et validation
        - EMPLOYE: saisie de temps uniquement

        Args:
            action: L'action à vérifier (ex: "creer_projet", "valider_temps")

        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        # ADMINISTRATEUR a toutes les permissions
        if self.role == RoleUtilisateur.ADMINISTRATEUR:
            return True

        # GESTIONNAIRE peut gérer les projets et valider
        if self.role == RoleUtilisateur.GESTIONNAIRE:
            actions_gestionnaire = [
                "creer_projet",
                "modifier_projet",
                "creer_tache",
                "modifier_tache",
                "valider_temps",
                "saisir_temps"
            ]
            return action in actions_gestionnaire

        # EMPLOYE peut seulement saisir son temps
        if self.role == RoleUtilisateur.EMPLOYE:
            actions_employe = ["saisir_temps", "consulter_projets"]
            return action in actions_employe

        return False

    def activer(self) -> None:
        """Active le compte utilisateur (logique métier)."""
        self.actif = True

    def desactiver(self) -> None:
        """Désactive le compte utilisateur (logique métier)."""
        self.actif = False

    def changer_role(self, nouveau_role: RoleUtilisateur) -> None:
        """
        Change le rôle de l'utilisateur.

        Args:
            nouveau_role: Le nouveau rôle à attribuer

        Raises:
            ValueError: Si le nouveau rôle est invalide
        """
        if not isinstance(nouveau_role, RoleUtilisateur):
            raise ValueError("Le rôle doit être un RoleUtilisateur valide")

        self.role = nouveau_role
