"""
Adapter primaire: Router FastAPI.
Expose les endpoints HTTP et fait le pont entre HTTP et le domaine.
Dépend du PORT PRIMAIRE (interface), pas directement du service.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from adapters.primary.fastapi.schemas.project_schemas import (
    CreateProjectRequest,
    ProjectResponse
)
from ports.primary.project_use_cases import ProjectUseCasesPort


# Création du router FastAPI
router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


def get_project_use_cases() -> ProjectUseCasesPort:
    """
    Dépendance FastAPI pour injecter les cas d'usage.

    IMPORTANT: Cette fonction sera remplacée par le DI container.
    C'est ici que l'injection de dépendances se produit.
    """
    from di_container import get_project_service
    return get_project_service()


# Type annotation pour l'injection de dépendances
ProjectUseCasesDep = Annotated[ProjectUseCasesPort, Depends(get_project_use_cases)]


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau projet",
    description="Crée un nouveau projet avec toutes les informations requises"
)
def create_project(
    request: CreateProjectRequest,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """
    Endpoint POST /api/projects

    Rôle de cet adapter:
    1. Recevoir la requête HTTP (FastAPI le fait automatiquement)
    2. Valider les données (Pydantic le fait automatiquement)
    3. Appeler le cas d'usage du domaine
    4. Convertir la réponse du domaine en DTO HTTP
    5. Gérer les erreurs et les convertir en codes HTTP appropriés

    Args:
        request: DTO validé par Pydantic
        use_cases: Service métier injecté (via le port primaire)

    Returns:
        DTO de réponse avec le projet créé

    Raises:
        HTTPException: En cas d'erreur métier ou technique
    """
    try:
        # Appel du cas d'usage du domaine (via le port primaire)
        project = use_cases.create_project(
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            comment=request.comment,
            manager_id=request.manager_id
        )

        # Conversion de l'entité domaine vers le DTO de réponse
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            budget=project.budget,
            comment=project.comment,
            manager_id=project.manager_id,
            is_active=project.is_active(),
            days_remaining=project.days_remaining()
        )

    except ValueError as e:
        # Erreur métier (validation, règles métier) → 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Erreur technique inattendue → 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du projet: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Récupérer un projet",
    description="Récupère les détails d'un projet par son ID"
)
def get_project(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """
    Endpoint GET /api/projects/{project_id}

    Args:
        project_id: ID du projet (extrait de l'URL par FastAPI)
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec le projet

    Raises:
        HTTPException: Si le projet n'existe pas
    """
    try:
        # Appel du cas d'usage
        project = use_cases.get_project(project_id)

        # Conversion vers DTO
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            budget=project.budget,
            comment=project.comment,
            manager_id=project.manager_id,
            is_active=project.is_active(),
            days_remaining=project.days_remaining()
        )

    except ValueError as e:
        # Projet non trouvé → 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Erreur technique
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du projet: {str(e)}"
        )
