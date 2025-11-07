"""
Tests d'intégration pour le repository SQLAlchemyUserRepository.

Ces tests vérifient l'interaction réelle avec une base de données.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.user import Utilisateur, RoleUtilisateur
from src.adapters.secondary.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
    UtilisateurModel,
    Base
)


@pytest.fixture(scope="function")
def db_session():
    """Session de test avec rollback automatique."""
    # Créer un moteur SQLite en mémoire pour les tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def user_repository(db_session):
    """Repository avec session de test."""
    return SQLAlchemyUserRepository(db_session)


def test_save_generates_id(user_repository):
    """Sauvegarder un utilisateur doit générer un ID."""
    utilisateur = Utilisateur(
        id=None,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    saved = user_repository.save(utilisateur)

    assert saved.id is not None
    assert saved.id > 0
    assert saved.nom == "Dupont"


def test_find_by_id_returns_user(user_repository, db_session):
    """find_by_id doit retourner l'utilisateur correct."""
    # Créer directement en base
    model = UtilisateurModel(
        nom="Martin",
        prenom="Marie",
        email="marie.martin@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.GESTIONNAIRE.value,
        date_creation=datetime.now(),
        actif=True
    )
    db_session.add(model)
    db_session.commit()

    # Tester
    found = user_repository.find_by_id(model.id)

    assert found is not None
    assert found.id == model.id
    assert found.nom == "Martin"
    assert found.email == "marie.martin@example.com"
    assert found.role == RoleUtilisateur.GESTIONNAIRE


def test_find_by_id_returns_none_if_not_found(user_repository):
    """find_by_id doit retourner None si l'utilisateur n'existe pas."""
    found = user_repository.find_by_id(999)

    assert found is None


def test_find_by_email_returns_user(user_repository):
    """find_by_email doit retourner l'utilisateur correct."""
    # Créer un utilisateur
    utilisateur = Utilisateur(
        id=None,
        nom="Durand",
        prenom="Pierre",
        email="pierre.durand@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    user_repository.save(utilisateur)

    # Tester
    found = user_repository.find_by_email("pierre.durand@example.com")

    assert found is not None
    assert found.email == "pierre.durand@example.com"
    assert found.nom == "Durand"


def test_find_by_email_is_case_insensitive(user_repository):
    """find_by_email doit être insensible à la casse."""
    # Créer un utilisateur
    utilisateur = Utilisateur(
        id=None,
        nom="Durand",
        prenom="Pierre",
        email="pierre.durand@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    user_repository.save(utilisateur)

    # Tester avec différentes casses
    found = user_repository.find_by_email("PIERRE.DURAND@EXAMPLE.COM")

    assert found is not None
    assert found.email == "pierre.durand@example.com"


def test_find_all_with_pagination(user_repository):
    """find_all doit retourner les utilisateurs avec pagination."""
    # Créer plusieurs utilisateurs
    for i in range(5):
        utilisateur = Utilisateur(
            id=None,
            nom=f"User{i}",
            prenom="Test",
            email=f"user{i}@example.com",
            mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        )
        user_repository.save(utilisateur)

    # Tester pagination
    page1 = user_repository.find_all(offset=0, limit=2)
    page2 = user_repository.find_all(offset=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].nom != page2[0].nom  # Pages différentes


def test_exists_by_email_returns_true_if_exists(user_repository):
    """exists_by_email doit retourner True si l'email existe."""
    # Créer un utilisateur
    utilisateur = Utilisateur(
        id=None,
        nom="Test",
        prenom="User",
        email="test@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    user_repository.save(utilisateur)

    # Tester
    exists = user_repository.exists_by_email("test@example.com")

    assert exists is True


def test_exists_by_email_returns_false_if_not_exists(user_repository):
    """exists_by_email doit retourner False si l'email n'existe pas."""
    exists = user_repository.exists_by_email("nonexistent@example.com")

    assert exists is False


def test_update_user(user_repository):
    """update doit modifier un utilisateur existant."""
    # Créer un utilisateur
    utilisateur = Utilisateur(
        id=None,
        nom="Original",
        prenom="User",
        email="original@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    saved = user_repository.save(utilisateur)

    # Modifier
    saved.nom = "Modified"
    saved.prenom = "Updated"
    updated = user_repository.update(saved)

    assert updated.nom == "Modified"
    assert updated.prenom == "Updated"
    assert updated.id == saved.id


def test_update_nonexistent_user_raises_error(user_repository):
    """update doit lever une erreur si l'utilisateur n'existe pas."""
    from src.domain.exceptions import EntityNotFoundError

    utilisateur = Utilisateur(
        id=999,
        nom="Nonexistent",
        prenom="User",
        email="nonexistent@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    with pytest.raises(EntityNotFoundError):
        user_repository.update(utilisateur)


def test_delete_user(user_repository):
    """delete doit supprimer un utilisateur."""
    # Créer un utilisateur
    utilisateur = Utilisateur(
        id=None,
        nom="ToDelete",
        prenom="User",
        email="todelete@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    saved = user_repository.save(utilisateur)

    # Supprimer
    result = user_repository.delete(saved.id)

    assert result is True

    # Vérifier que l'utilisateur n'existe plus
    found = user_repository.find_by_id(saved.id)
    assert found is None


def test_delete_nonexistent_user_returns_false(user_repository):
    """delete doit retourner False si l'utilisateur n'existe pas."""
    result = user_repository.delete(999)

    assert result is False
