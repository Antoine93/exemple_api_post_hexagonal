"""
Adapter secondaire: implémentation concrète du repository avec MySQL.
IMPLÉMENTE le port secondaire (ProjectRepositoryPort).
Contient le code technique d'accès aux données.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base

from domain.entities.project import Project
from ports.secondary.project_repository import ProjectRepositoryPort


# Modèle SQLAlchemy (ORM) - couche technique
Base = declarative_base()


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


class MySQLProjectRepository(ProjectRepositoryPort):
    """
    Implémentation MySQL du repository de projets.

    Cette classe contient UNIQUEMENT du code technique d'accès aux données.
    Aucune logique métier ici.
    """

    def __init__(self, db_session: Session):
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

    def find_all(self) -> List[Project]:
        """Récupère tous les projets depuis MySQL."""
        project_models = self._session.query(ProjectModel).all()
        return [self._to_domain(pm) for pm in project_models]

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
        return Project(
            id=project_model.id,
            name=project_model.name,
            description=project_model.description,
            start_date=project_model.start_date,
            end_date=project_model.end_date,
            budget=project_model.budget,
            comment=project_model.comment,
            manager_id=project_model.manager_id
        )
