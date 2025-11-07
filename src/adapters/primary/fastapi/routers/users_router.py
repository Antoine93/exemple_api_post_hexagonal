"""
Adapter primaire: Router FastAPI pour Utilisateur.

Expose les endpoints HTTP et fait le pont entre HTTP et le domaine.
Dépend du PORT PRIMAIRE (interface), pas directement du service.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List
import logging

from src.adapters.primary.fastapi.schemas.user_schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    ActivateUserRequest,
    ChangeRoleRequest,
    UserResponse
)
from src.ports.primary.user_use_cases import UserUseCasesPort
from src.domain.entities.user import RoleUtilisateur
from src.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    DomainValidationError
)

# Logger pour ce module
logger = logging.getLogger(__name__)

# Création du router FastAPI
router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


def get_user_use_cases() -> UserUseCasesPort:
    """
    Dépendance FastAPI pour injecter les cas d'usage.

    Cette fonction est appelée par FastAPI pour obtenir le service.
    C'est ici que l'injection de dépendances se produit.
    """
    from src.di_container import get_user_service
    return get_user_service()


# Type annotation pour l'injection de dépendances
UserUseCasesDep = Annotated[UserUseCasesPort, Depends(get_user_use_cases)]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel utilisateur",
    description="Crée un nouvel utilisateur avec toutes les informations requises"
)
def create_user(
    request: CreateUserRequest,
    use_cases: UserUseCasesDep
) -> UserResponse:
    """
    Endpoint POST /api/users

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
        DTO de réponse avec l'utilisateur créé

    Raises:
        HTTPException: En cas d'erreur métier ou technique
    """
    try:
        # Convertir le rôle string vers l'enum
        role_enum = RoleUtilisateur[request.role]

        # Appel du cas d'usage du domaine (via le port primaire)
        utilisateur = use_cases.creer_utilisateur(
            nom=request.nom,
            prenom=request.prenom,
            email=request.email,
            mot_de_passe=request.mot_de_passe,
            role=role_enum
        )

        # Conversion de l'entité domaine vers le DTO de réponse
        return UserResponse(
            id=utilisateur.id,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            role=utilisateur.role.value,
            date_creation=utilisateur.date_creation,
            actif=utilisateur.actif
        )

    except EntityAlreadyExistsError as e:
        # Conflit - l'utilisateur existe déjà
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except DomainValidationError as e:
        # Erreur de validation métier
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Erreur technique inattendue
        logger.error(
            "Unexpected error creating user",
            exc_info=True,
            extra={"email": request.email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Récupérer un utilisateur",
    description="Récupère les détails d'un utilisateur par son ID"
)
def get_user(
    user_id: int,
    use_cases: UserUseCasesDep
) -> UserResponse:
    """
    Endpoint GET /api/users/{user_id}

    Args:
        user_id: ID de l'utilisateur (extrait de l'URL par FastAPI)
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec l'utilisateur

    Raises:
        HTTPException: Si l'utilisateur n'existe pas
    """
    try:
        utilisateur = use_cases.obtenir_utilisateur(user_id)

        return UserResponse(
            id=utilisateur.id,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            role=utilisateur.role.value,
            date_creation=utilisateur.date_creation,
            actif=utilisateur.actif
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error("Unexpected error getting user", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Lister les utilisateurs",
    description="Liste tous les utilisateurs avec pagination"
)
def list_users(
    offset: int = Query(0, ge=0, description="Nombre d'utilisateurs à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre max d'utilisateurs"),
    use_cases: UserUseCasesDep
) -> List[UserResponse]:
    """
    Endpoint GET /api/users?offset=0&limit=20

    Liste les utilisateurs avec pagination.

    Args:
        offset: Nombre d'utilisateurs à sauter
        limit: Nombre maximum d'utilisateurs à retourner
        use_cases: Service métier injecté

    Returns:
        Liste de DTOs d'utilisateurs
    """
    try:
        utilisateurs = use_cases.lister_utilisateurs(offset=offset, limit=limit)

        return [
            UserResponse(
                id=u.id,
                nom=u.nom,
                prenom=u.prenom,
                email=u.email,
                role=u.role.value,
                date_creation=u.date_creation,
                actif=u.actif
            )
            for u in utilisateurs
        ]

    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error listing users", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Mettre à jour un utilisateur",
    description="Met à jour les informations d'un utilisateur existant"
)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    use_cases: UserUseCasesDep
) -> UserResponse:
    """
    Endpoint PUT /api/users/{user_id}

    Met à jour un utilisateur existant (PATCH sémantique - champs optionnels).

    Args:
        user_id: ID de l'utilisateur
        request: DTO avec les champs à modifier
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec l'utilisateur modifié
    """
    try:
        utilisateur = use_cases.modifier_utilisateur(
            user_id=user_id,
            nom=request.nom,
            prenom=request.prenom,
            email=request.email
        )

        return UserResponse(
            id=utilisateur.id,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            role=utilisateur.role.value,
            date_creation=utilisateur.date_creation,
            actif=utilisateur.actif
        )

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error updating user", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur",
    description="Supprime (désactive) un utilisateur"
)
def delete_user(
    user_id: int,
    use_cases: UserUseCasesDep
) -> None:
    """
    Endpoint DELETE /api/users/{user_id}

    Supprime (soft delete) un utilisateur.

    Args:
        user_id: ID de l'utilisateur à supprimer
        use_cases: Service métier injecté
    """
    try:
        use_cases.supprimer_utilisateur(user_id)

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error deleting user", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activer/Désactiver un utilisateur",
    description="Active ou désactive un utilisateur"
)
def activate_user(
    user_id: int,
    request: ActivateUserRequest,
    use_cases: UserUseCasesDep
) -> UserResponse:
    """
    Endpoint PATCH /api/users/{user_id}/activate

    Active ou désactive un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        request: DTO avec le statut actif
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec l'utilisateur modifié
    """
    try:
        utilisateur = use_cases.activer_desactiver_utilisateur(
            user_id=user_id,
            actif=request.actif
        )

        return UserResponse(
            id=utilisateur.id,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            role=utilisateur.role.value,
            date_creation=utilisateur.date_creation,
            actif=utilisateur.actif
        )

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error activating/deactivating user", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Changer le rôle d'un utilisateur",
    description="Change le rôle d'un utilisateur"
)
def change_user_role(
    user_id: int,
    request: ChangeRoleRequest,
    use_cases: UserUseCasesDep
) -> UserResponse:
    """
    Endpoint PATCH /api/users/{user_id}/role

    Change le rôle d'un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        request: DTO avec le nouveau rôle
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec l'utilisateur modifié
    """
    try:
        # Convertir le rôle string vers l'enum
        nouveau_role = RoleUtilisateur[request.role]

        utilisateur = use_cases.changer_role(
            user_id=user_id,
            nouveau_role=nouveau_role
        )

        return UserResponse(
            id=utilisateur.id,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            role=utilisateur.role.value,
            date_creation=utilisateur.date_creation,
            actif=utilisateur.actif
        )

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error changing user role", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.post(
    "/{user_id}/change-password",
    status_code=status.HTTP_200_OK,
    summary="Changer le mot de passe d'un utilisateur",
    description="Change le mot de passe d'un utilisateur après vérification de l'ancien"
)
def change_password(
    user_id: int,
    request: ChangePasswordRequest,
    use_cases: UserUseCasesDep
) -> dict:
    """
    Endpoint POST /api/users/{user_id}/change-password

    Change le mot de passe d'un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        request: DTO avec l'ancien et le nouveau mot de passe
        use_cases: Service métier injecté

    Returns:
        Message de succès
    """
    try:
        success = use_cases.changer_mot_de_passe(
            user_id=user_id,
            ancien_mot_de_passe=request.ancien_mot_de_passe,
            nouveau_mot_de_passe=request.nouveau_mot_de_passe
        )

        if success:
            return {"message": "Mot de passe changé avec succès"}

    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except DomainValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error changing password", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )
