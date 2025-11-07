"""
Tests unitaires pour l'entité Utilisateur.

Ces tests vérifient la logique métier de l'entité sans dépendances externes.
"""
import pytest
from datetime import datetime
from src.domain.entities.user import Utilisateur, RoleUtilisateur


def test_utilisateur_creation_valide():
    """Une entité Utilisateur valide doit être créée sans erreur."""
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe("Password123!")

    utilisateur = Utilisateur(
        id=None,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=mot_de_passe_hash,
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.nom == "Dupont"
    assert utilisateur.prenom == "Jean"
    assert utilisateur.email == "jean.dupont@example.com"
    assert utilisateur.role == RoleUtilisateur.EMPLOYE
    assert utilisateur.actif is True


def test_utilisateur_rejette_nom_vide():
    """Un nom vide doit lever une ValueError."""
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe("Password123!")

    with pytest.raises(ValueError, match="Le nom ne peut pas être vide"):
        Utilisateur(
            id=None,
            nom="",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe_hash=mot_de_passe_hash,
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        )


def test_utilisateur_rejette_prenom_vide():
    """Un prénom vide doit lever une ValueError."""
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe("Password123!")

    with pytest.raises(ValueError, match="Le prénom ne peut pas être vide"):
        Utilisateur(
            id=None,
            nom="Dupont",
            prenom="",
            email="jean.dupont@example.com",
            mot_de_passe_hash=mot_de_passe_hash,
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        )


def test_utilisateur_rejette_email_invalide():
    """Un email invalide doit lever une ValueError."""
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe("Password123!")

    with pytest.raises(ValueError, match="L'email n'est pas au format valide"):
        Utilisateur(
            id=None,
            nom="Dupont",
            prenom="Jean",
            email="email_invalide",
            mot_de_passe_hash=mot_de_passe_hash,
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        )


def test_utilisateur_rejette_mot_de_passe_hash_invalide():
    """Un hash de mot de passe invalide doit lever une ValueError."""
    with pytest.raises(ValueError, match="Le mot de passe doit être hashé en SHA-256"):
        Utilisateur(
            id=None,
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe_hash="hash_trop_court",
            role=RoleUtilisateur.EMPLOYE,
            date_creation=datetime.now(),
            actif=True
        )


def test_hash_mot_de_passe_genere_sha256():
    """La méthode hash_mot_de_passe doit générer un hash SHA-256 de 64 caractères."""
    mot_de_passe = "Password123!"
    hash_resultat = Utilisateur.hash_mot_de_passe(mot_de_passe)

    assert len(hash_resultat) == 64
    assert isinstance(hash_resultat, str)


def test_hash_mot_de_passe_rejette_mot_de_passe_court():
    """Un mot de passe trop court doit lever une ValueError."""
    with pytest.raises(ValueError, match="au moins 8 caractères"):
        Utilisateur.hash_mot_de_passe("court")


def test_verifier_mot_de_passe_correct():
    """La vérification d'un mot de passe correct doit retourner True."""
    mot_de_passe = "Password123!"
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe(mot_de_passe)

    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=mot_de_passe_hash,
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.verifier_mot_de_passe(mot_de_passe) is True


def test_verifier_mot_de_passe_incorrect():
    """La vérification d'un mot de passe incorrect doit retourner False."""
    mot_de_passe = "Password123!"
    mot_de_passe_hash = Utilisateur.hash_mot_de_passe(mot_de_passe)

    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=mot_de_passe_hash,
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.verifier_mot_de_passe("MauvaisMotDePasse") is False


def test_activer_utilisateur():
    """La méthode activer() doit mettre actif à True."""
    utilisateur = Utilisateur(
        id=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=False
    )

    utilisateur.activer()
    assert utilisateur.actif is True


def test_desactiver_utilisateur():
    """La méthode desactiver() doit mettre actif à False."""
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

    utilisateur.desactiver()
    assert utilisateur.actif is False


def test_verifier_permission_administrateur():
    """Un ADMINISTRATEUR doit avoir toutes les permissions."""
    utilisateur = Utilisateur(
        id=1,
        nom="Admin",
        prenom="Super",
        email="admin@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.ADMINISTRATEUR,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.verifier_permission("creer_projet") is True
    assert utilisateur.verifier_permission("supprimer_projet") is True
    assert utilisateur.verifier_permission("toute_action") is True


def test_verifier_permission_gestionnaire():
    """Un GESTIONNAIRE doit avoir des permissions limitées."""
    utilisateur = Utilisateur(
        id=1,
        nom="Gestionnaire",
        prenom="Manager",
        email="manager@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.GESTIONNAIRE,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.verifier_permission("creer_projet") is True
    assert utilisateur.verifier_permission("modifier_projet") is True
    assert utilisateur.verifier_permission("valider_temps") is True
    assert utilisateur.verifier_permission("action_inconnue") is False


def test_verifier_permission_employe():
    """Un EMPLOYE doit avoir des permissions très limitées."""
    utilisateur = Utilisateur(
        id=1,
        nom="Employe",
        prenom="Worker",
        email="worker@example.com",
        mot_de_passe_hash=Utilisateur.hash_mot_de_passe("Password123!"),
        role=RoleUtilisateur.EMPLOYE,
        date_creation=datetime.now(),
        actif=True
    )

    assert utilisateur.verifier_permission("saisir_temps") is True
    assert utilisateur.verifier_permission("consulter_projets") is True
    assert utilisateur.verifier_permission("creer_projet") is False
    assert utilisateur.verifier_permission("valider_temps") is False


def test_changer_role():
    """La méthode changer_role() doit modifier le rôle."""
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

    utilisateur.changer_role(RoleUtilisateur.GESTIONNAIRE)
    assert utilisateur.role == RoleUtilisateur.GESTIONNAIRE
