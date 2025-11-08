"""
Adapter secondaire: implémentation concrète du repository avec SQLAlchemy.
IMPLÉMENTE le port secondaire (ProjectRepositoryPort).
Contient le code technique d'accès aux données.
Compatible avec SQLite, MySQL, PostgreSQL, etc. grâce à SQLAlchemy.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Date, Text, Boolean, Integer, DateTime, ForeignKey

from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType
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

    Correspond au schéma défini dans documents/05_database_schema.puml
    """
    __tablename__ = "projets"

    # Identifiant
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Informations de base
    numero: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Dates
    date_debut: Mapped[datetime] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[datetime] = mapped_column(Date, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Type et état
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    stade: Mapped[str] = mapped_column(String(100), nullable=True)
    commentaire: Mapped[str] = mapped_column(Text, nullable=True)

    # Heures
    heures_planifiees: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    heures_reelles: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Template
    est_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    projet_template_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("projets.id"),
        nullable=True
    )

    # Relations (IDs seulement - pas de relations ORM pour l'instant)
    responsable_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entreprise_id: Mapped[int] = mapped_column(Integer, nullable=False)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


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
        Sauvegarde un projet dans la base de données.

        Conversion: Entité domaine → Modèle ORM → DB
        """
        # Conversion de l'entité domaine vers le modèle ORM
        project_model = ProjectModel(
            numero=project.numero,
            nom=project.nom,
            description=project.description,
            date_debut=project.date_debut,
            date_echeance=project.date_echeance,
            date_creation=project.date_creation,
            type=project.type.value,  # Convertir l'enum en string
            stade=project.stade,
            commentaire=project.commentaire,
            heures_planifiees=project.heures_planifiees,
            heures_reelles=project.heures_reelles,
            est_template=project.est_template,
            projet_template_id=project.projet_template_id,
            responsable_id=project.responsable_id,
            entreprise_id=project.entreprise_id,
            contact_id=project.contact_id
        )

        # Opération technique de persistance
        self._session.add(project_model)
        self._session.commit()
        self._session.refresh(project_model)

        # Conversion du modèle ORM vers l'entité domaine
        return self._to_domain(project_model)

    def find_by_id(self, project_id: int) -> Optional[Project]:
        """Récupère un projet par ID depuis la base de données."""
        project_model = self._session.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()

        if project_model is None:
            return None

        return self._to_domain(project_model)

    def find_all(self, offset: int = 0, limit: int = 20) -> list[Project]:
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

        # Mettre à jour tous les champs
        project_model.numero = project.numero
        project_model.nom = project.nom
        project_model.description = project.description
        project_model.date_debut = project.date_debut
        project_model.date_echeance = project.date_echeance
        project_model.type = project.type.value
        project_model.stade = project.stade
        project_model.commentaire = project.commentaire
        project_model.heures_planifiees = project.heures_planifiees
        project_model.heures_reelles = project.heures_reelles
        project_model.est_template = project.est_template
        project_model.projet_template_id = project.projet_template_id
        project_model.responsable_id = project.responsable_id
        project_model.entreprise_id = project.entreprise_id
        project_model.contact_id = project.contact_id
        # date_creation ne change JAMAIS

        # Sauvegarder les changements
        self._session.commit()
        self._session.refresh(project_model)

        # Convertir et retourner
        return self._to_domain(project_model)

    def exists_by_name(self, name: str) -> bool:
        """Vérifie si un projet avec ce nom existe."""
        count = self._session.query(ProjectModel).filter(
            ProjectModel.nom == name
        ).count()
        return count > 0

    def exists_by_numero(self, numero: str) -> bool:
        """Vérifie si un projet avec ce numéro existe."""
        count = self._session.query(ProjectModel).filter(
            ProjectModel.numero == numero
        ).count()
        return count > 0

    def delete(self, project_id: int) -> bool:
        """Supprime un projet de la base de données."""
        project_model = self._session.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()

        if project_model is None:
            return False

        self._session.delete(project_model)
        self._session.commit()
        return True

    def find_templates(self) -> list[Project]:
        """Récupère tous les projets templates."""
        project_models = self._session.query(ProjectModel).filter(
            ProjectModel.est_template == True
        ).all()

        return [self._to_domain(pm) for pm in project_models]

    def find_by_template_id(self, template_id: int) -> list[Project]:
        """Trouve tous les projets créés depuis un template spécifique."""
        project_models = self._session.query(ProjectModel).filter(
            ProjectModel.projet_template_id == template_id
        ).all()

        return [self._to_domain(pm) for pm in project_models]

    def find_by_entreprise(self, entreprise_id: int) -> list[Project]:
        """Trouve tous les projets d'une entreprise."""
        project_models = self._session.query(ProjectModel).filter(
            ProjectModel.entreprise_id == entreprise_id
        ).all()

        return [self._to_domain(pm) for pm in project_models]

    def find_by_responsable(self, responsable_id: int) -> list[Project]:
        """Trouve tous les projets d'un responsable."""
        project_models = self._session.query(ProjectModel).filter(
            ProjectModel.responsable_id == responsable_id
        ).all()

        return [self._to_domain(pm) for pm in project_models]

    def _to_domain(self, project_model: ProjectModel) -> Project:
        """
        Convertit un modèle ORM en entité du domaine.

        IMPORTANT: Cette méthode isole le domaine de la couche technique.
        """
        # Convertir les types SQLAlchemy Date en datetime.date Python si nécessaire
        date_debut = project_model.date_debut
        if isinstance(date_debut, datetime):
            date_debut = date_debut.date()

        date_echeance = project_model.date_echeance
        if isinstance(date_echeance, datetime):
            date_echeance = date_echeance.date()

        return Project(
            id=int(project_model.id) if project_model.id is not None else None,
            numero=str(project_model.numero),
            nom=str(project_model.nom),
            description=str(project_model.description),
            date_debut=date_debut,
            date_echeance=date_echeance,
            date_creation=project_model.date_creation,
            type=ProjectType(project_model.type),  # Convertir string en enum
            stade=str(project_model.stade) if project_model.stade else None,
            commentaire=str(project_model.commentaire) if project_model.commentaire else None,
            heures_planifiees=float(project_model.heures_planifiees),
            heures_reelles=float(project_model.heures_reelles),
            est_template=bool(project_model.est_template),
            projet_template_id=int(project_model.projet_template_id) if project_model.projet_template_id else None,
            responsable_id=int(project_model.responsable_id),
            entreprise_id=int(project_model.entreprise_id),
            contact_id=int(project_model.contact_id) if project_model.contact_id else None
        )
