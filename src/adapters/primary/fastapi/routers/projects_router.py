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
    ProjectResponse,
    DupliquerProjetRequest,
    CreerDepuisTemplateRequest,
    AvancementResponse,
    EcartTempsResponse
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


def _project_to_response(project) -> ProjectResponse:
    """Convertit une entité Project du domaine en DTO de réponse."""
    return ProjectResponse(
        id=project.id,
        numero=project.numero,
        nom=project.nom,
        description=project.description,
        date_debut=project.date_debut,
        date_echeance=project.date_echeance,
        date_creation=project.date_creation,
        type=project.type,
        stade=project.stade,
        commentaire=project.commentaire,
        heures_planifiees=project.heures_planifiees,
        heures_reelles=project.heures_reelles,
        est_template=project.est_template,
        projet_template_id=project.projet_template_id,
        responsable_id=project.responsable_id,
        entreprise_id=project.entreprise_id,
        contact_id=project.contact_id,
        # Champs calculés
        is_active=project.is_active(),
        days_remaining=project.days_remaining(),
        avancement=project.calculer_avancement(),
        ecart_temps=project.calculer_ecart_temps(),
        est_en_retard=project.est_en_retard()
    )


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

    Crée un nouveau projet dans le système.
    """
    try:
        project = use_cases.create_project(
            numero=request.numero,
            nom=request.nom,
            description=request.description,
            date_debut=request.date_debut,
            date_echeance=request.date_echeance,
            type=request.type,
            stade=request.stade,
            commentaire=request.commentaire,
            heures_planifiees=request.heures_planifiees,
            heures_reelles=request.heures_reelles,
            est_template=request.est_template,
            projet_template_id=request.projet_template_id,
            responsable_id=request.responsable_id,
            entreprise_id=request.entreprise_id,
            contact_id=request.contact_id
        )

        return _project_to_response(project)

    except ProjectAlreadyExistsError as e:
        logger.warning(f"Tentative de création d'un projet existant: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (ValueError, DomainValidationError) as e:
        logger.warning(f"Validation error lors de la création: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la création: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Récupérer un projet",
    description="Récupère un projet par son ID"
)
def get_project(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """Endpoint GET /api/projects/{project_id}"""
    try:
        project = use_cases.get_project(project_id)
        return _project_to_response(project)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Lister les projets",
    description="Récupère la liste des projets avec pagination"
)
def list_projects(
    use_cases: ProjectUseCasesDep,
    offset: int = Query(0, ge=0, description="Nombre de projets à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de projets")
) -> list[ProjectResponse]:
    """Endpoint GET /api/projects"""
    try:
        projects = use_cases.list_projects(offset=offset, limit=limit)
        return [_project_to_response(p) for p in projects]

    except Exception as e:
        logger.error(f"Erreur lors de la liste: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Mettre à jour un projet",
    description="Met à jour un projet existant (tous les champs optionnels)"
)
def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """Endpoint PUT /api/projects/{project_id}"""
    try:
        project = use_cases.update_project(
            project_id=project_id,
            numero=request.numero,
            nom=request.nom,
            description=request.description,
            date_debut=request.date_debut,
            date_echeance=request.date_echeance,
            type=request.type,
            stade=request.stade,
            commentaire=request.commentaire,
            heures_planifiees=request.heures_planifiees,
            heures_reelles=request.heures_reelles,
            est_template=request.est_template,
            projet_template_id=request.projet_template_id,
            responsable_id=request.responsable_id,
            entreprise_id=request.entreprise_id,
            contact_id=request.contact_id
        )

        return _project_to_response(project)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (ValueError, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un projet",
    description="Supprime un projet par son ID"
)
def delete_project(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> None:
    """Endpoint DELETE /api/projects/{project_id}"""
    try:
        use_cases.delete_project(project_id)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


# ===== NOUVEAUX ENDPOINTS POUR LES TEMPLATES ET DUPLICATION =====


@router.get(
    "/templates/list",
    response_model=list[ProjectResponse],
    summary="Lister les templates",
    description="Récupère tous les projets templates"
)
def list_templates(
    use_cases: ProjectUseCasesDep
) -> list[ProjectResponse]:
    """Endpoint GET /api/projects/templates/list"""
    try:
        templates = use_cases.find_templates()
        return [_project_to_response(t) for t in templates]

    except Exception as e:
        logger.error(f"Erreur lors de la liste des templates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.post(
    "/{project_id}/duplicate",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dupliquer un projet",
    description="Crée une copie d'un projet existant avec de nouvelles informations"
)
def duplicate_project(
    project_id: int,
    request: DupliquerProjetRequest,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """Endpoint POST /api/projects/{project_id}/duplicate"""
    try:
        project = use_cases.dupliquer_projet(
            project_id=project_id,
            nouveau_numero=request.nouveau_numero,
            nouveau_nom=request.nouveau_nom,
            nouvelle_date_debut=request.nouvelle_date_debut,
            nouvelle_date_echeance=request.nouvelle_date_echeance
        )

        return _project_to_response(project)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet source avec l'ID {project_id} introuvable"
        )
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (ValueError, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.post(
    "/{project_id}/save-as-template",
    response_model=ProjectResponse,
    summary="Sauvegarder comme template",
    description="Transforme un projet existant en template réutilisable"
)
def save_as_template(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """Endpoint POST /api/projects/{project_id}/save-as-template"""
    try:
        project = use_cases.sauvegarder_comme_template(project_id)
        return _project_to_response(project)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.post(
    "/from-template/{template_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer depuis un template",
    description="Crée un nouveau projet à partir d'un template existant"
)
def create_from_template(
    template_id: int,
    request: CreerDepuisTemplateRequest,
    use_cases: ProjectUseCasesDep
) -> ProjectResponse:
    """Endpoint POST /api/projects/from-template/{template_id}"""
    try:
        project = use_cases.creer_depuis_template(
            template_id=template_id,
            numero=request.numero,
            nom=request.nom,
            date_debut=request.date_debut,
            date_echeance=request.date_echeance,
            responsable_id=request.responsable_id,
            entreprise_id=request.entreprise_id,
            contact_id=request.contact_id
        )

        return _project_to_response(project)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template avec l'ID {template_id} introuvable"
        )
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        # Cas où le projet n'est pas un template
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


# ===== ENDPOINTS POUR LES CALCULS =====


@router.get(
    "/{project_id}/avancement",
    response_model=AvancementResponse,
    summary="Calculer l'avancement",
    description="Calcule le pourcentage d'avancement d'un projet"
)
def get_avancement(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> AvancementResponse:
    """Endpoint GET /api/projects/{project_id}/avancement"""
    try:
        # Un seul appel au service pour récupérer le projet
        project = use_cases.get_project(project_id)

        # Calcul de l'avancement via la méthode métier de l'entité
        avancement = project.calculer_avancement()

        return AvancementResponse(
            project_id=project_id,
            heures_planifiees=project.heures_planifiees,
            heures_reelles=project.heures_reelles,
            avancement_pourcentage=avancement
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True, extra={"project_id": project_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.get(
    "/{project_id}/ecart-temps",
    response_model=EcartTempsResponse,
    summary="Calculer l'écart temps",
    description="Calcule l'écart entre heures planifiées et réelles"
)
def get_ecart_temps(
    project_id: int,
    use_cases: ProjectUseCasesDep
) -> EcartTempsResponse:
    """Endpoint GET /api/projects/{project_id}/ecart-temps"""
    try:
        # Un seul appel au service pour récupérer le projet
        project = use_cases.get_project(project_id)

        # Calcul de l'écart via la méthode métier de l'entité
        ecart = project.calculer_ecart_temps()

        # Calcul du pourcentage d'écart
        ecart_pourcentage = 0.0
        if project.heures_planifiees > 0:
            ecart_pourcentage = (ecart / project.heures_planifiees) * 100

        return EcartTempsResponse(
            project_id=project_id,
            heures_planifiees=project.heures_planifiees,
            heures_reelles=project.heures_reelles,
            ecart=ecart,
            ecart_pourcentage=ecart_pourcentage
        )

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projet avec l'ID {project_id} introuvable"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True, extra={"project_id": project_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
