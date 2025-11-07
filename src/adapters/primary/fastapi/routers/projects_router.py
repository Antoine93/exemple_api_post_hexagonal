"""
Adapter primaire: Router FastAPI.
Expose les endpoints HTTP et fait le pont entre HTTP et le domaine.
Dépend du PORT PRIMAIRE (interface), pas directement du service.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from src.adapters.primary.fastapi.schemas.project_schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse
)
from src.domain.exceptions import (
    DomainValidationError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError
)
from src.ports.primary.project_use_cases import ProjectUseCasesPort

# Configure logger for this module
logger = logging.getLogger(__name__)


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
    from src.di_container import get_project_service
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

    except ProjectAlreadyExistsError as e:
        # Duplicate name → 409 Conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except DomainValidationError as e:
        # Domain validation error → 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        # Entity validation error → 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected error → 500 with generic message
        logger.error(f"Unexpected error creating project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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

    except ProjectNotFoundError as e:
        # Project not found → 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected error → 500 with generic message
        logger.error(f"Unexpected error retrieving project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Lister les projets",
    description="Liste tous les projets avec pagination"
)
def list_projects(
    use_cases: ProjectUseCasesDep,
    offset: int = Query(0, ge=0, description="Nombre de projets à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de projets à retourner")
) -> list[ProjectResponse]:
    """
    Endpoint GET /api/projects

    Args:
        offset: Pagination offset
        limit: Pagination limit
        use_cases: Service métier injecté

    Returns:
        Liste de projets
    """
    try:
        # Appel du cas d'usage
        projects = use_cases.list_projects(offset=offset, limit=limit)

        # Conversion vers DTOs
        return [
            ProjectResponse(
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
            for project in projects
        ]

    except Exception as e:
        # Unexpected error → 500 with generic message
        logger.error(f"Unexpected error listing projects: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Mettre à jour un projet",
    description="Met à jour un projet existant (tous les champs sont optionnels)"
)
def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """
    Endpoint PUT /api/projects/{project_id}

    Args:
        project_id: ID du projet à mettre à jour
        request: DTO avec les champs à mettre à jour
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec le projet mis à jour

    Raises:
        HTTPException: En cas d'erreur métier ou technique
    """
    try:
        # Appel du cas d'usage
        project = use_cases.update_project(
            project_id=project_id,
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            comment=request.comment,
            manager_id=request.manager_id
        )

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

    except ProjectNotFoundError as e:
        # Project not found → 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProjectAlreadyExistsError as e:
        # Duplicate name → 409 Conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except DomainValidationError as e:
        # Domain validation error → 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        # Entity validation error → 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected error → 500 with generic message
        logger.error(f"Unexpected error updating project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un projet",
    description="Supprime un projet existant"
)
def delete_project(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> None:
    """
    Endpoint DELETE /api/projects/{project_id}

    Args:
        project_id: ID du projet à supprimer
        use_cases: Service métier injecté

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: Si le projet n'existe pas
    """
    try:
        # Appel du cas d'usage
        use_cases.delete_project(project_id)

    except ProjectNotFoundError as e:
        # Project not found → 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected error → 500 with generic message
        logger.error(f"Unexpected error deleting project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
