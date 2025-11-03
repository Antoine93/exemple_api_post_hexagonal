"""
DI Container: Point central d'injection de dépendances.

C'est ici que:
1. Les dépendances sont créées
2. Les implémentations concrètes sont liées aux interfaces
3. Le câblage de l'application se fait

IMPORTANT: Seul ce fichier connaît les implémentations concrètes.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from domain.services.project_service import ProjectService
from adapters.secondary.repositories.mysql_project_repository import (
    MySQLProjectRepository,
    Base
)
from ports.primary.project_use_cases import ProjectUseCasesPort


# Configuration de la base de données
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/project_db"

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Création des tables (en production, utiliser Alembic pour les migrations)
Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """
    Factory pour créer une session de base de données.

    Returns:
        Session SQLAlchemy
    """
    return SessionLocal()


def get_project_repository() -> MySQLProjectRepository:
    """
    Factory pour créer le repository de projets.

    Ici, on choisit l'implémentation concrète (MySQL).
    On pourrait facilement changer pour PostgreSQL, MongoDB, etc.

    Returns:
        Implémentation concrète du ProjectRepositoryPort
    """
    db_session = get_db_session()
    return MySQLProjectRepository(db_session)


def get_project_service() -> ProjectUseCasesPort:
    """
    Factory pour créer le service de projets.

    C'est ici que l'INJECTION DE DÉPENDANCES se produit:
    - On crée le repository (adapter secondaire)
    - On l'injecte dans le service (domaine)
    - On retourne le service via son interface (port primaire)

    Returns:
        Service métier (via l'interface ProjectUseCasesPort)
    """
    # 1. Créer l'adapter secondaire (implémentation concrète)
    repository = get_project_repository()

    # 2. Injecter dans le service du domaine
    service = ProjectService(project_repository=repository)

    # 3. Retourner via l'interface (port primaire)
    return service


# Alternative: Utiliser une bibliothèque comme dependency-injector
# from dependency_injector import containers, providers
#
# class Container(containers.DeclarativeContainer):
#     db_session = providers.Singleton(get_db_session)
#     project_repository = providers.Factory(
#         MySQLProjectRepository,
#         db_session=db_session
#     )
#     project_service = providers.Factory(
#         ProjectService,
#         project_repository=project_repository
#     )
