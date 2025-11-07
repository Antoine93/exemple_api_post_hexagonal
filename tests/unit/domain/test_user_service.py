"""
Tests unitaires pour le service UserService.

Ces tests vérifient la logique métier du service avec des mocks de repository.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from src.domain.entities.user import Utilisateur, RoleUtilisateur
from src.domain.services.user_service import UserService
from src.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    DomainValidationError
)
from src.ports.secondary.user_repository import UserRepositoryPort


@pytest.fixture
def mock_user_repository():
    """Mock du repository pour tests unitaires."""
    return Mock(spec=UserRepositoryPort)


@pytest.fixture
def user_service(mock_user_repository):
    """Service avec repository mocké."""
    return UserService(mock_user_repository)


def test_creer_utilisateur_success(user_service, mock_user_repository):
    """Créer un utilisateur avec succès."""
    # Arrange
    mock_user_repository.exists_by_email.return_value = False
    mock_user_repository.save.return_value = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    # Act
    resultat = user_service.creer_utilisateur(
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe="Password123!",
        role=RoleUtilisateur.EMPLOYE
    )

    # Assert
    assert resultat.id == 1
    assert resultat.nom == "Dupont"
    assert resultat.email == "jean.dupont@example.com"
    mock_user_repository.exists_by_email.assert_called_once_with("jean.dupont@example.com")
    mock_user_repository.save.assert_called_once()


def test_creer_utilisateur_email_existe(user_service, mock_user_repository):
    """Ne pas créer un utilisateur si l'email existe déjà."""
    # Arrange
    mock_user_repository.exists_by_email.return_value = True

    # Act & Assert
    with pytest.raises(EntityAlreadyExistsError, match="existe déjà"):
        user_service.creer_utilisateur(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe="Password123!",
            role=RoleUtilisateur.EMPLOYE
        )

    # Vérifier que save n'a pas été appelé
    mock_user_repository.save.assert_not_called()


def test_creer_utilisateur_mot_de_passe_trop_court(user_service, mock_user_repository):
    """Rejeter un mot de passe trop court."""
    # Arrange
    mock_user_repository.exists_by_email.return_value = False

    # Act & Assert
    with pytest.raises(DomainValidationError, match="au moins 8 caractères"):
        user_service.creer_utilisateur(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe="court",
            role=RoleUtilisateur.EMPLOYE
        )


def test_obtenir_utilisateur_success(user_service, mock_user_repository):
    """Récupérer un utilisateur par son ID."""
    # Arrange
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur

    # Act
    resultat = user_service.obtenir_utilisateur(1)

    # Assert
    assert resultat.id == 1
    assert resultat.nom == "Dupont"
    mock_user_repository.find_by_id.assert_called_once_with(1)


def test_obtenir_utilisateur_introuvable(user_service, mock_user_repository):
    """Lever EntityNotFoundError si l'utilisateur n'existe pas."""
    # Arrange
    mock_user_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError, match="introuvable"):
        user_service.obtenir_utilisateur(999)


def test_lister_utilisateurs_success(user_service, mock_user_repository):
    """Lister les utilisateurs avec pagination."""
    # Arrange
    utilisateurs = [
        Utilisateur(
            id=1,
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        ),
        Utilisateur(
            id=2,
            nom="Martin",
            prenom="Marie",
            email="marie.martin@example.com",
            mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
            role=RoleUtilisateur.GESTIONNAIRE,
            date_creation=datetime.now(),
            actif=True
        )
    ]
    mock_user_repository.find_all.return_value = utilisateurs

    # Act
    resultat = user_service.lister_utilisateurs(offset=0, limit=20)

    # Assert
    assert len(resultat) == 2
    assert resultat[0].nom == "Dupont"
    assert resultat[1].nom == "Martin"
    mock_user_repository.find_all.assert_called_once_with(offset=0, limit=20)


def test_lister_utilisateurs_offset_negatif(user_service):
    """Rejeter un offset négatif."""
    with pytest.raises(DomainValidationError, match="ne peut pas être négatif"):
        user_service.lister_utilisateurs(offset=-1, limit=20)


def test_lister_utilisateurs_limit_invalide(user_service):
    """Rejeter une limite invalide."""
    with pytest.raises(DomainValidationError, match="entre 1 et 100"):
        user_service.lister_utilisateurs(offset=0, limit=200)


def test_modifier_utilisateur_success(user_service, mock_user_repository):
    """Modifier un utilisateur avec succès."""
    # Arrange
    utilisateur_existant = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur_existant
    mock_user_repository.exists_by_email.return_value = False
    mock_user_repository.update.return_value = utilisateur_existant

    # Act
    resultat = user_service.modifier_utilisateur(
        user_id=1,
        nom="Durand",
        prenom="Pierre"
    )

    # Assert
    assert resultat.nom == "Durand"
    assert resultat.prenom == "Pierre"
    mock_user_repository.update.assert_called_once()


def test_modifier_utilisateur_email_existe(user_service, mock_user_repository):
    """Rejeter la modification si le nouvel email existe déjà."""
    # Arrange
    utilisateur_existant = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur_existant
    mock_user_repository.exists_by_email.return_value = True

    # Act & Assert
    with pytest.raises(EntityAlreadyExistsError):
        user_service.modifier_utilisateur(
            user_id=1,
            email="autre.email@example.com"
        )


def test_supprimer_utilisateur_success(user_service, mock_user_repository):
    """Supprimer (désactiver) un utilisateur avec succès."""
    # Arrange
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur
    mock_user_repository.update.return_value = utilisateur

    # Act
    resultat = user_service.supprimer_utilisateur(1)

    # Assert
    assert resultat is True
    assert utilisateur.actif is False
    mock_user_repository.update.assert_called_once()


def test_activer_desactiver_utilisateur(user_service, mock_user_repository):
    """Activer/désactiver un utilisateur."""
    # Arrange
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur
    mock_user_repository.update.return_value = utilisateur

    # Act - Désactiver
    resultat = user_service.activer_desactiver_utilisateur(1, False)

    # Assert
    assert resultat.actif is False

    # Act - Activer
    resultat = user_service.activer_desactiver_utilisateur(1, True)

    # Assert
    assert resultat.actif is True


def test_changer_role_success(user_service, mock_user_repository):
    """Changer le rôle d'un utilisateur."""
    # Arrange
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur
    mock_user_repository.update.return_value = utilisateur

    # Act
    resultat = user_service.changer_role(1, RoleUtilisateur.GESTIONNAIRE)

    # Assert
    assert resultat.role == RoleUtilisateur.GESTIONNAIRE
    mock_user_repository.update.assert_called_once()


def test_changer_mot_de_passe_success(user_service, mock_user_repository):
    """Changer le mot de passe d'un utilisateur."""
    # Arrange
    ancien_mdp = "Password123!"
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe(ancien_mdp),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur
    mock_user_repository.update.return_value = utilisateur

    # Act
    resultat = user_service.changer_mot_de_passe(
        user_id=1,
        ancien_mot_de_passe=ancien_mdp,
        nouveau_mot_de_passe="NewPassword456!"
    )

    # Assert
    assert resultat is True
    assert utilisateur.verifier_mot_de_passe("NewPassword456!") is True
    mock_user_repository.update.assert_called_once()


def test_changer_mot_de_passe_ancien_incorrect(user_service, mock_user_repository):
    """Rejeter le changement si l'ancien mot de passe est incorrect."""
    # Arrange
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )
    mock_user_repository.find_by_id.return_value = utilisateur

    # Act & Assert
    with pytest.raises(DomainValidationError, match="ancien mot de passe est incorrect"):
        user_service.changer_mot_de_passe(
            user_id=1,
            ancien_mot_de_passe="MauvaisMotDePasse",
            nouveau_mot_de_passe="NewPassword456!"
        )
