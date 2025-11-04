"""
DI Container: Point central d'injection de dépendances.

C'est ici que:
1. Les dépendances sont créées
2. Les implémentations concrètes sont liées aux interfaces
3. Le câblage de l'application se fait

IMPORTANT: Seul ce fichier connaît les implémentations concrètes.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.domain.services.project_service import ProjectService
from src.adapters.secondary.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
    Base
)
from src.ports.primary.project_use_cases import ProjectUseCasesPort

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration de la base de données
# Par défaut: SQLite (aucune installation requise, parfait pour le développement)
# Pour MySQL: définir DATABASE_URL dans le fichier .env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./project_db.sqlite"  # Valeur par défaut: SQLite
)

print(f"📊 Utilisation de la base de données: {DATABASE_URL.split('://')[0].upper()}")

# Configuration spécifique pour SQLite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # Pour SQLite: activer les foreign keys et utiliser check_same_thread=False
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "echo": True
    }
else:
    # Pour MySQL/PostgreSQL
    engine_kwargs = {"echo": True}

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine)

# Création des tables (en production, utiliser Alembic pour les migrations)
Base.metadata.create_all(bind=engine)
print("✅ Tables de base de données créées/vérifiées")


def get_db_session() -> Session:
    """
    Factory pour créer une session de base de données.

    Returns:
        Session SQLAlchemy
    """
    return SessionLocal()


def get_project_repository() -> SQLAlchemyProjectRepository:
    """
    Factory pour créer le repository de projets.

    Ici, on choisit l'implémentation concrète (SQLAlchemy).
    SQLAlchemy supporte: SQLite, MySQL, PostgreSQL, Oracle, etc.
    Pour changer de BDD: modifier DATABASE_URL dans .env

    Returns:
        Implémentation concrète du ProjectRepositoryPort
    """
    db_session = get_db_session()
    return SQLAlchemyProjectRepository(db_session)


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
#         SQLAlchemyProjectRepository,
#         db_session=db_session
#     )
#     project_service = providers.Factory(
#         ProjectService,
#         project_repository=project_repository
#     )
