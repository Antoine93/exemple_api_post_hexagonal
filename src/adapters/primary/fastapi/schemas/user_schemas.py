"""
Schemas Pydantic pour Utilisateur.

Ces DTOs (Data Transfer Objects) définissent la structure
des requêtes/réponses HTTP. Ils appartiennent à la couche adapter.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class CreateUserRequest(BaseModel):
    """
    DTO pour la requête de création d'utilisateur.

    FastAPI utilise ce schema pour:
    - Valider les données d'entrée HTTP
    - Générer la documentation OpenAPI
    """
    nom: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nom de famille de l'utilisateur"
    )
    prenom: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Prénom de l'utilisateur"
    )
    email: str = Field(
        ...,
        description="Adresse email (unique)",
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    mot_de_passe: str = Field(
        ...,
        min_length=8,
        description="Mot de passe (minimum 8 caractères)"
    )
    role: str = Field(
        ...,
        description="Rôle de l'utilisateur (ADMINISTRATEUR, GESTIONNAIRE, EMPLOYE)"
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validation du rôle (format HTTP, pas métier)."""
        valid_roles = ["ADMINISTRATEUR", "GESTIONNAIRE", "EMPLOYE"]
        if v.upper() not in valid_roles:
            raise ValueError(
                f"Le rôle doit être l'un des suivants: {', '.join(valid_roles)}"
            )
        return v.upper()


class UpdateUserRequest(BaseModel):
    """
    DTO pour la requête de mise à jour d'utilisateur.

    Tous les champs sont optionnels (PATCH sémantique).
    """
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(
        None,
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )


class ChangePasswordRequest(BaseModel):
    """
    DTO pour la requête de changement de mot de passe.
    """
    ancien_mot_de_passe: str = Field(
        ...,
        description="L'ancien mot de passe (pour vérification)"
    )
    nouveau_mot_de_passe: str = Field(
        ...,
        min_length=8,
        description="Le nouveau mot de passe (minimum 8 caractères)"
    )


class ActivateUserRequest(BaseModel):
    """
    DTO pour activer/désactiver un utilisateur.
    """
    actif: bool = Field(
        ...,
        description="True pour activer, False pour désactiver"
    )


class ChangeRoleRequest(BaseModel):
    """
    DTO pour changer le rôle d'un utilisateur.
    """
    role: str = Field(
        ...,
        description="Nouveau rôle (ADMINISTRATEUR, GESTIONNAIRE, EMPLOYE)"
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validation du rôle."""
        valid_roles = ["ADMINISTRATEUR", "GESTIONNAIRE", "EMPLOYE"]
        if v.upper() not in valid_roles:
            raise ValueError(
                f"Le rôle doit être l'un des suivants: {', '.join(valid_roles)}"
            )
        return v.upper()


class UserResponse(BaseModel):
    """
    DTO pour la réponse contenant un utilisateur.

    Ce schema définit la structure JSON retournée par l'API.
    """
    id: int
    nom: str
    prenom: str
    email: str
    role: str
    date_creation: datetime
    actif: bool

    class Config:
        """Configuration Pydantic."""
        from_attributes = True
