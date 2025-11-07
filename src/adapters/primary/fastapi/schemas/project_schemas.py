"""
Schemas Pydantic: DTOs (Data Transfer Objects) pour FastAPI.
Ces classes définissent la structure des requêtes/réponses HTTP.
Elles appartiennent à la couche adapter primaire (FastAPI).
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, Any


class CreateProjectRequest(BaseModel):
    """
    DTO pour la requête de création de projet.

    FastAPI utilise ce schema pour:
    - Valider les données d'entrée HTTP
    - Générer la documentation OpenAPI
    """
    name: str = Field(..., min_length=1, max_length=255, description="Nom du projet")
    description: str = Field(..., min_length=1, description="Description du projet")
    start_date: date = Field(..., description="Date de début du projet")
    end_date: date = Field(..., description="Date de fin du projet")
    budget: float = Field(..., gt=0, description="Budget du projet (doit être positif)")
    comment: Optional[str] = Field(None, description="Commentaire optionnel")
    manager_id: int = Field(..., gt=0, description="ID du gestionnaire responsable")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date: date, info: Any) -> date:
        """Validation supplémentaire: end_date > start_date."""
        start_date = info.data.get('start_date')
        if start_date and end_date <= start_date:
            raise ValueError("La date de fin doit être après la date de début")
        return end_date


class UpdateProjectRequest(BaseModel):
    """
    DTO pour la requête de mise à jour de projet.

    Tous les champs sont optionnels - seuls les champs fournis seront mis à jour.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nouveau nom du projet")
    description: Optional[str] = Field(None, min_length=1, description="Nouvelle description")
    start_date: Optional[date] = Field(None, description="Nouvelle date de début")
    end_date: Optional[date] = Field(None, description="Nouvelle date de fin")
    budget: Optional[float] = Field(None, gt=0, description="Nouveau budget (doit être positif)")
    comment: Optional[str] = Field(None, description="Nouveau commentaire")
    manager_id: Optional[int] = Field(None, gt=0, description="Nouvel ID du gestionnaire")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date: Optional[date], info: Any) -> Optional[date]:
        """Validation: si end_date et start_date sont fournis, end_date > start_date."""
        if end_date is None:
            return end_date

        start_date = info.data.get('start_date')
        if start_date and end_date <= start_date:
            raise ValueError("La date de fin doit être après la date de début")
        return end_date


class ProjectResponse(BaseModel):
    """
    DTO pour la réponse contenant un projet.

    Ce schema définit la structure JSON retournée par l'API.

    Note: In practice, id should always be present in responses since
    we only return projects that have been saved to the database.
    However, the domain entity allows Optional[int] to support
    unsaved entities, so we maintain that flexibility here.
    """
    id: Optional[int]
    name: str
    description: str
    start_date: date
    end_date: date
    budget: float
    comment: Optional[str]
    manager_id: int
    is_active: bool
    days_remaining: int

    class Config:
        """Configuration Pydantic."""
        from_attributes = True  # Permet la conversion depuis des objets Python
