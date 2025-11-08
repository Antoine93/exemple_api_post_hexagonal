"""
Schemas Pydantic: DTOs (Data Transfer Objects) pour FastAPI.
Ces classes définissent la structure des requêtes/réponses HTTP.
Elles appartiennent à la couche adapter primaire (FastAPI).
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

# Import de l'enum du domaine - une seule source de vérité
from src.domain.entities.project_type import ProjectType


class CreateProjectRequest(BaseModel):
    """
    DTO pour la requête de création de projet.

    FastAPI utilise ce schema pour:
    - Valider les données d'entrée HTTP
    - Générer la documentation OpenAPI
    """
    numero: str = Field(..., min_length=1, max_length=50, description="Numéro unique du projet")
    nom: str = Field(..., min_length=1, max_length=255, description="Nom du projet")
    description: str = Field(..., min_length=1, description="Description du projet")
    date_debut: date = Field(..., description="Date de début du projet")
    date_echeance: date = Field(..., description="Date d'échéance du projet")
    type: ProjectType = Field(..., description="Type de projet")
    stade: Optional[str] = Field(None, max_length=100, description="Stade actuel du projet")
    commentaire: Optional[str] = Field(None, description="Commentaire optionnel")
    heures_planifiees: float = Field(..., ge=0, description="Heures planifiées (>= 0)")
    heures_reelles: float = Field(default=0.0, ge=0, description="Heures réelles (>= 0)")
    est_template: bool = Field(default=False, description="Indique si c'est un template")
    projet_template_id: Optional[int] = Field(None, description="ID du template source")
    responsable_id: int = Field(..., gt=0, description="ID du responsable")
    entreprise_id: int = Field(..., gt=0, description="ID de l'entreprise")
    contact_id: Optional[int] = Field(None, gt=0, description="ID du contact principal")


class UpdateProjectRequest(BaseModel):
    """
    DTO pour la requête de mise à jour de projet.

    Tous les champs sont optionnels - seuls les champs fournis seront mis à jour.
    """
    numero: Optional[str] = Field(None, min_length=1, max_length=50, description="Nouveau numéro")
    nom: Optional[str] = Field(None, min_length=1, max_length=255, description="Nouveau nom")
    description: Optional[str] = Field(None, min_length=1, description="Nouvelle description")
    date_debut: Optional[date] = Field(None, description="Nouvelle date de début")
    date_echeance: Optional[date] = Field(None, description="Nouvelle date d'échéance")
    type: Optional[ProjectType] = Field(None, description="Nouveau type")
    stade: Optional[str] = Field(None, max_length=100, description="Nouveau stade")
    commentaire: Optional[str] = Field(None, description="Nouveau commentaire")
    heures_planifiees: Optional[float] = Field(None, ge=0, description="Nouvelles heures planifiées")
    heures_reelles: Optional[float] = Field(None, ge=0, description="Nouvelles heures réelles")
    est_template: Optional[bool] = Field(None, description="Modifier le statut template")
    projet_template_id: Optional[int] = Field(None, description="Modifier le template source")
    responsable_id: Optional[int] = Field(None, gt=0, description="Nouveau responsable")
    entreprise_id: Optional[int] = Field(None, gt=0, description="Nouvelle entreprise")
    contact_id: Optional[int] = Field(None, gt=0, description="Nouveau contact")


class DupliquerProjetRequest(BaseModel):
    """DTO pour dupliquer un projet."""
    nouveau_numero: str = Field(..., min_length=1, max_length=50, description="Numéro du nouveau projet")
    nouveau_nom: str = Field(..., min_length=1, max_length=255, description="Nom du nouveau projet")
    nouvelle_date_debut: date = Field(..., description="Date de début du nouveau projet")
    nouvelle_date_echeance: date = Field(..., description="Date d'échéance du nouveau projet")


class CreerDepuisTemplateRequest(BaseModel):
    """DTO pour créer un projet depuis un template."""
    numero: str = Field(..., min_length=1, max_length=50, description="Numéro unique du projet")
    nom: str = Field(..., min_length=1, max_length=255, description="Nom du projet")
    date_debut: date = Field(..., description="Date de début")
    date_echeance: date = Field(..., description="Date d'échéance")
    responsable_id: int = Field(..., gt=0, description="ID du responsable")
    entreprise_id: int = Field(..., gt=0, description="ID de l'entreprise")
    contact_id: Optional[int] = Field(None, gt=0, description="ID du contact")


class ProjectResponse(BaseModel):
    """
    DTO pour la réponse contenant un projet.

    Ce schema définit la structure JSON retournée par l'API.
    """
    id: Optional[int]
    numero: str
    nom: str
    description: str
    date_debut: date
    date_echeance: date
    date_creation: datetime
    type: ProjectType
    stade: Optional[str]
    commentaire: Optional[str]
    heures_planifiees: float
    heures_reelles: float
    est_template: bool
    projet_template_id: Optional[int]
    responsable_id: int
    entreprise_id: int
    contact_id: Optional[int]

    # Champs calculés
    is_active: bool
    days_remaining: int
    avancement: float
    ecart_temps: float
    est_en_retard: bool

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class AvancementResponse(BaseModel):
    """DTO pour la réponse du calcul d'avancement."""
    project_id: int
    heures_planifiees: float
    heures_reelles: float
    avancement_pourcentage: float


class EcartTempsResponse(BaseModel):
    """DTO pour la réponse du calcul d'écart temps."""
    project_id: int
    heures_planifiees: float
    heures_reelles: float
    ecart: float
    ecart_pourcentage: float


class ProjectListResponse(BaseModel):
    """DTO pour une liste de projets avec pagination."""
    projects: list[ProjectResponse]
    total: int
    offset: int
    limit: int
