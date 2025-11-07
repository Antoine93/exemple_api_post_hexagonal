"""
Tests end-to-end pour l'API Utilisateurs.

Ces tests vérifient le fonctionnement complet de l'API via HTTP.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.di_container import get_db_session
from src.adapters.secondary.repositories.sqlalchemy_project_repository import Base


# Fixture pour la base de données de test
@pytest.fixture(scope="function", autouse=False)
def test_db():
    """Créer une base de données de test en mémoire ISOLÉE pour chaque test."""
    # Créer un nouveau moteur avec un nom unique pour forcer l'isolation
    import uuid
    db_name = f"file:test_{uuid.uuid4().hex}?mode=memory&cache=shared"
    engine = create_engine(
        f"sqlite:///{db_name}",
        connect_args={"check_same_thread": False, "uri": True}
    )

    # Créer toutes les tables dans cette base isolée
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        """Override de la session DB pour les tests."""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    # Override de la dépendance FastAPI
    app.dependency_overrides[get_db_session] = override_get_db

    yield engine

    # Cleanup complet après le test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_db):
    """Client de test FastAPI avec base de données isolée."""
    return TestClient(app)


def test_create_user_success(client):
    """POST /api/users doit créer un utilisateur et retourner 201."""
    response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Dupont"
    assert data["prenom"] == "Jean"
    assert data["email"] == "jean.dupont@example.com"
    assert data["role"] == "EMPLOYE"
    assert data["actif"] is True
    assert "id" in data
    assert "date_creation" in data


def test_create_user_duplicate_email_returns_409(client):
    """POST /api/users avec un email existant doit retourner 409."""
    # Créer un premier utilisateur
    client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "unique@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })

    # Tenter de créer un second utilisateur avec le même email
    response = client.post("/api/users", json={
        "nom": "Martin",
        "prenom": "Marie",
        "email": "unique@example.com",
        "mot_de_passe": "Password456!",
        "role": "GESTIONNAIRE"
    })

    assert response.status_code == 409
    assert "existe déjà" in response.json()["detail"]


def test_create_user_invalid_password_returns_400(client):
    """POST /api/users avec un mot de passe invalide doit retourner 400."""
    response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "court",
        "role": "EMPLOYE"
    })

    assert response.status_code == 422  # Validation Pydantic


def test_create_user_invalid_role_returns_422(client):
    """POST /api/users avec un rôle invalide doit retourner 422."""
    response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "ROLE_INVALIDE"
    })

    assert response.status_code == 422


def test_get_user_success(client):
    """GET /api/users/{id} doit retourner 200 avec l'utilisateur."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Récupérer l'utilisateur
    response = client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["nom"] == "Dupont"
    assert data["email"] == "jean.dupont@example.com"


def test_get_user_not_found_returns_404(client):
    """GET /api/users/{id} avec un ID inexistant doit retourner 404."""
    response = client.get("/api/users/999")

    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"]


def test_list_users_success(client):
    """GET /api/users doit retourner la liste des utilisateurs."""
    # Créer plusieurs utilisateurs
    for i in range(3):
        client.post("/api/users", json={
            "nom": f"User{i}",
            "prenom": "Test",
            "email": f"user{i}@example.com",
            "mot_de_passe": "Password123!",
            "role": "EMPLOYE"
        })

    # Lister les utilisateurs
    response = client.get("/api/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["nom"] == "User0"


def test_list_users_with_pagination(client):
    """GET /api/users avec pagination doit fonctionner."""
    # Créer 5 utilisateurs
    for i in range(5):
        client.post("/api/users", json={
            "nom": f"User{i}",
            "prenom": "Test",
            "email": f"user{i}@example.com",
            "mot_de_passe": "Password123!",
            "role": "EMPLOYE"
        })

    # Page 1
    response1 = client.get("/api/users?offset=0&limit=2")
    assert response1.status_code == 200
    assert len(response1.json()) == 2

    # Page 2
    response2 = client.get("/api/users?offset=2&limit=2")
    assert response2.status_code == 200
    assert len(response2.json()) == 2


def test_update_user_success(client):
    """PUT /api/users/{id} doit mettre à jour l'utilisateur."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Mettre à jour
    response = client.put(f"/api/users/{user_id}", json={
        "nom": "Durand",
        "prenom": "Pierre"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "Durand"
    assert data["prenom"] == "Pierre"
    assert data["email"] == "jean.dupont@example.com"  # Inchangé


def test_update_user_not_found_returns_404(client):
    """PUT /api/users/{id} avec un ID inexistant doit retourner 404."""
    response = client.put("/api/users/999", json={
        "nom": "Nouveau"
    })

    assert response.status_code == 404


def test_delete_user_success(client):
    """DELETE /api/users/{id} doit désactiver l'utilisateur."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Supprimer
    response = client.delete(f"/api/users/{user_id}")

    assert response.status_code == 204

    # Vérifier que l'utilisateur est désactivé
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["actif"] is False


def test_activate_user_success(client):
    """PATCH /api/users/{id}/activate doit activer/désactiver l'utilisateur."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Désactiver
    response = client.patch(f"/api/users/{user_id}/activate", json={
        "actif": False
    })

    assert response.status_code == 200
    assert response.json()["actif"] is False

    # Réactiver
    response = client.patch(f"/api/users/{user_id}/activate", json={
        "actif": True
    })

    assert response.status_code == 200
    assert response.json()["actif"] is True


def test_change_role_success(client):
    """PATCH /api/users/{id}/role doit changer le rôle."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Changer le rôle
    response = client.patch(f"/api/users/{user_id}/role", json={
        "role": "GESTIONNAIRE"
    })

    assert response.status_code == 200
    assert response.json()["role"] == "GESTIONNAIRE"


def test_change_password_success(client):
    """POST /api/users/{id}/change-password doit changer le mot de passe."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Changer le mot de passe
    response = client.post(f"/api/users/{user_id}/change-password", json={
        "ancien_mot_de_passe": "Password123!",
        "nouveau_mot_de_passe": "NewPassword456!"
    })

    assert response.status_code == 200
    assert "succès" in response.json()["message"]


def test_change_password_wrong_old_password_returns_400(client):
    """POST /api/users/{id}/change-password avec mauvais ancien mdp doit retourner 400."""
    # Créer un utilisateur
    create_response = client.post("/api/users", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mot_de_passe": "Password123!",
        "role": "EMPLOYE"
    })
    user_id = create_response.json()["id"]

    # Changer le mot de passe avec mauvais ancien
    response = client.post(f"/api/users/{user_id}/change-password", json={
        "ancien_mot_de_passe": "MauvaisMotDePasse",
        "nouveau_mot_de_passe": "NewPassword456!"
    })

    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"]
