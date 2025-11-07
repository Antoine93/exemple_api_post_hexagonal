"""
Adapter secondaire: implémentation SQLAlchemy du repository pour Utilisateur.

Implémente UserRepositoryPort avec SQLAlchemy.
Compatible: SQLite, MySQL, PostgreSQL, Oracle, etc.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SQLEnum

from src.domain.entities.user import Utilisateur, RoleUtilisateur
from src.ports.secondary.user_repository import UserRepositoryPort
from src.adapters.secondary.repositories.sqlalchemy_project_repository import Base


class UtilisateurModel(Base):
    """
    Modèle de table SQL pour Utilisateur.

    IMPORTANT: Ce n'est PAS l'entité du domaine.
    C'est un modèle technique pour la persistance.
    """
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SQLEnum(RoleUtilisateur, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    date_creation: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SQLAlchemyUserRepository(UserRepositoryPort):
    """
    Implémentation SQLAlchemy du repository pour Utilisateur.

    Cette classe contient UNIQUEMENT du code technique d'accès aux données.
    Aucune logique métier ici.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Injection de la session SQLAlchemy.

        Args:
            db_session: Session SQLAlchemy pour les opérations DB
        """
        self._session = db_session

    def save(self, user: Utilisateur) -> Utilisateur:
        """
        Sauvegarde un utilisateur dans la base de données.

        Conversion: Entité domaine → Modèle ORM → DB
        """
        # Conversion de l'entité domaine vers le modèle ORM
        model = UtilisateurModel(
            nom=user.nom,
            prenom=user.prenom,
            email=user.email,
            mot_de_passe_hash=user.mot_de_passe_hash,
            role=user.role.value,
            date_creation=user.date_creation,
            actif=user.actif
        )

        # Opération technique de persistance
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        # Conversion du modèle ORM vers l'entité domaine
        return self._to_domain(model)

    def find_by_id(self, user_id: int) -> Optional[Utilisateur]:
        """Récupère un utilisateur par ID depuis la base."""
        model = self._session.query(UtilisateurModel).filter(
            UtilisateurModel.id == user_id
        ).first()

        if model is None:
            return None

        return self._to_domain(model)

    def find_by_email(self, email: str) -> Optional[Utilisateur]:
        """Récupère un utilisateur par email depuis la base."""
        model = self._session.query(UtilisateurModel).filter(
            UtilisateurModel.email == email.lower()
        ).first()

        if model is None:
            return None

        return self._to_domain(model)

    def find_all(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[Utilisateur]:
        """Récupère tous les utilisateurs avec pagination."""
        models = self._session.query(UtilisateurModel)\
            .offset(offset)\
            .limit(limit)\
            .all()

        return [self._to_domain(model) for model in models]

    def exists_by_email(self, email: str) -> bool:
        """Vérifie si un utilisateur avec cet email existe."""
        count = self._session.query(UtilisateurModel).filter(
            UtilisateurModel.email == email.lower()
        ).count()
        return count > 0

    def update(self, user: Utilisateur) -> Utilisateur:
        """Met à jour un utilisateur existant."""
        model = self._session.query(UtilisateurModel).filter(
            UtilisateurModel.id == user.id
        ).first()

        if model is None:
            from src.domain.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Utilisateur avec ID {user.id} introuvable")

        # Mise à jour des champs
        model.nom = user.nom
        model.prenom = user.prenom
        model.email = user.email
        model.mot_de_passe_hash = user.mot_de_passe_hash
        model.role = user.role.value
        model.actif = user.actif

        self._session.commit()
        self._session.refresh(model)

        return self._to_domain(model)

    def delete(self, user_id: int) -> bool:
        """
        Supprime un utilisateur de la base (hard delete).

        Note: Dans la pratique, on préfère un soft delete (désactivation)
        géré par le service métier.
        """
        model = self._session.query(UtilisateurModel).filter(
            UtilisateurModel.id == user_id
        ).first()

        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    def _to_domain(self, model: UtilisateurModel) -> Utilisateur:
        """
        Convertit un modèle ORM en entité du domaine.

        IMPORTANT: Cette méthode isole le domaine de la couche technique.

        Args:
            model: Le modèle SQLAlchemy

        Returns:
            L'entité du domaine
        """
        return Utilisateur(
            id=model.id,
            nom=model.nom,
            prenom=model.prenom,
            email=model.email,
            mot_de_passe_hash=model.mot_de_passe_hash,
            role=RoleUtilisateur(model.role),
            date_creation=model.date_creation,
            actif=model.actif
        )
