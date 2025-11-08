"""
End-to-end tests for the FastAPI application.

Tests complete user workflows through the HTTP API.
Uses TestClient to simulate HTTP requests without running the actual server.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta

from src.main import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    import uuid
    # Generate unique test ID for this test session to avoid name collisions
    test_id = str(uuid.uuid4())[:8]
    client = TestClient(app)
    client.test_id = test_id
    return client


class TestCreateProjectEndpoint:
    """Test suite for POST /api/projects endpoint."""

    def test_create_project_success(self, client):
        """Test successful project creation returns 201 with complete data."""
        # Arrange
        today = date.today()
        project_data = {
            "numero": f"PROJ-API-{client.test_id}",
            "nom": f"Test API Project {client.test_id}",
            "description": "A project created via API",
            "date_debut": today.isoformat(),
            "date_echeance": (today + timedelta(days=30)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": "Test comment",
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }

        # Act
        response = client.post("/api/projects", json=project_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert f"Test API Project {client.test_id}" in data["nom"]
        assert data["description"] == "A project created via API"
        assert data["heures_planifiees"] == 100.0
        assert data["responsable_id"] == 1
        assert data["entreprise_id"] == 1
        assert "is_active" in data
        assert "days_remaining" in data
        assert "avancement" in data
        assert "ecart_temps" in data
        assert "est_en_retard" in data

    def test_create_project_duplicate_numero_returns_409(self, client):
        """Test that creating a project with duplicate numero returns 409 Conflict."""
        # Arrange
        today = date.today()
        project_data = {
            "numero": f"PROJ-DUP-NUM-{client.test_id}",
            "nom": f"Duplicate Numero Project {client.test_id}",
            "description": "First project",
            "date_debut": today.isoformat(),
            "date_echeance": (today + timedelta(days=30)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": None,
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }

        # Create first project
        response1 = client.post("/api/projects", json=project_data)
        assert response1.status_code == 201

        # Act - Try to create duplicate numero (different name)
        project_data["nom"] = f"Different Name {client.test_id}"
        response2 = client.post("/api/projects", json=project_data)

        # Assert
        assert response2.status_code == 409
        assert "numéro" in response2.json()["detail"]

    def test_create_project_duplicate_name_returns_409(self, client):
        """Test that creating a project with duplicate name returns 409 Conflict."""
        # Arrange
        today = date.today()
        project_data = {
            "numero": f"PROJ-DUP-NOM-1-{client.test_id}",
            "nom": f"Duplicate Name Project {client.test_id}",
            "description": "First project",
            "date_debut": today.isoformat(),
            "date_echeance": (today + timedelta(days=30)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": None,
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }

        # Create first project
        response1 = client.post("/api/projects", json=project_data)
        assert response1.status_code == 201

        # Act - Try to create duplicate name (different numero)
        project_data["numero"] = f"PROJ-DUP-NOM-2-{client.test_id}"
        response2 = client.post("/api/projects", json=project_data)

        # Assert
        assert response2.status_code == 409
        assert "nom" in response2.json()["detail"]

    def test_create_project_invalid_heures_returns_422(self, client):
        """Test that negative heures_planifiees returns 422 validation error."""
        # Arrange
        today = date.today()
        project_data = {
            "numero": f"PROJ-INV-HEURES-{client.test_id}",
            "nom": "Invalid Heures Project",
            "description": "Has negative heures",
            "date_debut": today.isoformat(),
            "date_echeance": (today + timedelta(days=30)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": None,
            "heures_planifiees": -50.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }

        # Act
        response = client.post("/api/projects", json=project_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("heures" in str(error).lower() for error in errors)

    def test_create_project_invalid_dates_returns_422(self, client):
        """Test that date_echeance before date_debut returns 422."""
        # Arrange
        today = date.today()
        project_data = {
            "numero": f"PROJ-INV-DATES-{client.test_id}",
            "nom": "Invalid Dates Project",
            "description": "Has invalid dates",
            "date_debut": today.isoformat(),
            "date_echeance": (today - timedelta(days=10)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": None,
            "heures_planifiees": 100.0,
            "heures_reelles": 0.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }

        # Act
        response = client.post("/api/projects", json=project_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("date" in str(error).lower() for error in errors)


class TestGetProjectEndpoint:
    """Test suite for GET /api/projects/{id} endpoint."""

    def test_get_project_success(self, client):
        """Test successful project retrieval returns 200 with data."""
        # Arrange - Create a project first
        today = date.today()
        project_data = {
            "numero": f"PROJ-RETRIEVE-{client.test_id}",
            "nom": f"Project to Retrieve {client.test_id}",
            "description": "Will be retrieved",
            "date_debut": today.isoformat(),
            "date_echeance": (today + timedelta(days=30)).isoformat(),
            "type": "INTERNE",
            "stade": "En cours",
            "commentaire": "Retrieve me",
            "heures_planifiees": 150.0,
            "heures_reelles": 50.0,
            "est_template": False,
            "projet_template_id": None,
            "responsable_id": 1,
            "entreprise_id": 1,
            "contact_id": None
        }
        create_response = client.post("/api/projects", json=project_data)
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Act
        response = client.get(f"/api/projects/{project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert f"Project to Retrieve {client.test_id}" in data["nom"]
        assert data["is_active"] is True
        assert data["days_remaining"] >= 0
        assert data["avancement"] > 0  # Should have some progress since heures_reelles > 0
        assert "ecart_temps" in data
        assert "est_en_retard" in data

    def test_get_project_not_found_returns_404(self, client):
        """Test that getting non-existent project returns 404."""
        # Arrange
        non_existent_id = 99999

        # Act
        response = client.get(f"/api/projects/{non_existent_id}")

        # Assert
        assert response.status_code == 404
        assert "introuvable" in response.json()["detail"].lower()


class TestAPIDocumentation:
    """Test suite for API documentation endpoints."""

    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        # Act
        response = client.get("/openapi.json")

        # Assert
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Project & User Management API"

    def test_swagger_ui_accessible(self, client):
        """Test that Swagger UI documentation is accessible."""
        # Act
        response = client.get("/docs")

        # Assert
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "<!doctype html>" in response.text.lower()

    def test_redoc_accessible(self, client):
        """Test that ReDoc documentation is accessible."""
        # Act
        response = client.get("/redoc")

        # Assert
        assert response.status_code == 200
        assert "redoc" in response.text.lower() or "<!doctype html>" in response.text.lower()
