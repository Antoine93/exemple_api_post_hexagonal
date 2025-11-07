"""
Adapter secondaire: implémentation concrète du repository avec SQLAlchemy.
IMPLÉMENTE le port secondaire (ProjectRepositoryPort).
Contient le code technique d'accès aux données.
Compatible avec SQLite, MySQL, PostgreSQL, etc. grâce à SQLAlchemy.
"""
from typing import Optional, List, Any
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Date, Text

from src.domain.entities.project import Project
from src.ports.secondary.project_repository import ProjectRepositoryPort


# Modèle SQLAlchemy (ORM) - couche technique
class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass


class ProjectModel(Base):
    """
    Modèle de table SQL pour les projets.

    IMPORTANT: Ce n'est PAS l'entité du domaine, c'est un modèle technique
    pour la persistance. On fait la conversion entre ProjectModel et Project.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    manager_id = Column(Integer, nullable=False)


class SQLAlchemyProjectRepository(ProjectRepositoryPort):
    """
    Implémentation SQLAlchemy du repository de projets.

    Cette classe contient UNIQUEMENT du code technique d'accès aux données.
    Aucune logique métier ici.

    Compatible avec: SQLite, MySQL, PostgreSQL, Oracle, etc.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Injection de la session SQLAlchemy.

        Args:
            db_session: Session SQLAlchemy pour les opérations DB
        """
        self._session = db_session

    def save(self, project: Project) -> Project:
        """
        Sauvegarde un projet dans MySQL.

        Conversion: Entité domaine → Modèle ORM → DB
        """
        # Conversion de l'entité domaine vers le modèle ORM
        project_model = ProjectModel(
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            budget=project.budget,
            comment=project.comment,
            manager_id=project.manager_id
        )

        # Opération technique de persistance
        self._session.add(project_model)
        self._session.commit()
        self._session.refresh(project_model)

        # Conversion du modèle ORM vers l'entité domaine
        return self._to_domain(project_model)

    def find_by_id(self, project_id: int) -> Optional[Project]:
        """Récupère un projet par ID depuis MySQL."""
        project_model = self._session.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()

        if project_model is None:
            return None

        return self._to_domain(project_model)

    def find_all(self, offset: int = 0, limit: int = 20) -> List[Project]:
        """
        Récupère tous les projets avec pagination.

        Args:
            offset: Nombre de projets à ignorer
            limit: Nombre maximum de projets à retourner

        Returns:
            Liste de projets (peut être vide)
        """
        project_models = (
            self._session.query(ProjectModel)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(pm) for pm in project_models]

    def update(self, project: Project) -> Project:
        """
        Met à jour un projet existant dans la base de données.

        Args:
            project: L'entité Project avec les nouvelles valeurs

        Returns:
            Le projet mis à jour

        Raises:
            ValueError: Si le projet n'existe pas
        """
        # Récupérer le modèle existant
        project_model = self._session.query(ProjectModel).filter(
            ProjectModel.id == project.id
        ).first()

        if project_model is None:
            raise ValueError(f"Project with id {project.id} not found")

        # Mettre à jour les champs
        project_model.name = project.name  # type: ignore[assignment]
        project_model.description = project.description  # type: ignore[assignment]
        project_model.start_date = project.start_date  # type: ignore[assignment]
        project_model.end_date = project.end_date  # type: ignore[assignment]
        project_model.budget = project.budget  # type: ignore[assignment]
        project_model.comment = project.comment  # type: ignore[assignment]
        project_model.manager_id = project.manager_id  # type: ignore[assignment]

        # Sauvegarder les changements
        self._session.commit()
        self._session.refresh(project_model)

        # Convertir et retourner
        return self._to_domain(project_model)

    def exists_by_name(self, name: str) -> bool:
        """Vérifie si un projet avec ce nom existe."""
        count = self._session.query(ProjectModel).filter(
            ProjectModel.name == name
        ).count()
        return count > 0

    def delete(self, project_id: int) -> bool:
        """Supprime un projet de MySQL."""
        project_model = self._session.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()

        if project_model is None:
            return False

        self._session.delete(project_model)
        self._session.commit()
        return True

    def _to_domain(self, project_model: ProjectModel) -> Project:
        """
        Convertit un modèle ORM en entité du domaine.

        IMPORTANT: Cette méthode isole le domaine de la couche technique.
        """
        # SQLAlchemy's Column attributes are accessed as regular Python types at runtime
        # We need to cast them explicitly for mypy
        return Project(
            id=int(project_model.id) if project_model.id is not None else None,
            name=str(project_model.name),
            description=str(project_model.description),
            start_date=project_model.start_date,  # type: ignore[arg-type]
            end_date=project_model.end_date,  # type: ignore[arg-type]
            budget=float(project_model.budget),
            comment=str(project_model.comment) if project_model.comment else None,
            manager_id=int(project_model.manager_id)
        )
