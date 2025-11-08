"""
E2E tests for complete CRUD operations on the API.

Tests the UPDATE, DELETE, and LIST endpoints.
"""
import pytest
import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def unique_name():
    """Generate a unique project name for each test."""
    return f"Project-{uuid.uuid4().hex[:8]}"


class TestUpdateProjectEndpoint:
    """Test suite for PUT /api/projects/{id} endpoint."""

    def test_update_project_nom_success(self, client: TestClient, unique_name: str):
        """Test updating only the project nom."""
        # Arrange: Create a project first
        today = date.today()
        original_name = f"{unique_name}-original"
        updated_name = f"{unique_name}-updated"

        create_response = client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-UPD-NOM-{uuid.uuid4().hex[:8]}",
                "nom": original_name,
                "description": "Test project",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
                "type": "INTERNE",
                "stade": "En cours",
                "commentaire": "Original comment",
                "heures_planifiees": 100.0,
                "heures_reelles": 0.0,
                "est_template": False,
                "projet_template_id": None,
                "responsable_id": 1,
                "entreprise_id": 1,
                "contact_id": None
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Act: Update the nom
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={"nom": updated_name}
        )

        # Assert
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["nom"] == updated_name
        assert data["description"] == "Test project"  # Unchanged
        assert data["heures_planifiees"] == 100.0  # Unchanged

    def test_update_project_multiple_fields(self, client: TestClient, unique_name: str):
        """Test updating multiple fields at once."""
        # Arrange: Create a project
        today = date.today()
        name = f"{unique_name}-multi"

        create_response = client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-UPD-MULTI-{uuid.uuid4().hex[:8]}",
                "nom": name,
                "description": "Original description",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
                "type": "INTERNE",
                "stade": "En cours",
                "commentaire": "Original comment",
                "heures_planifiees": 100.0,
                "heures_reelles": 0.0,
                "est_template": False,
                "projet_template_id": None,
                "responsable_id": 1,
                "entreprise_id": 1,
                "contact_id": None
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Act: Update multiple fields
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={
                "description": "Updated description",
                "heures_planifiees": 200.0,
                "heures_reelles": 50.0,
                "commentaire": "Updated comment"
            }
        )

        # Assert
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["nom"] == name  # Unchanged
        assert data["description"] == "Updated description"
        assert data["heures_planifiees"] == 200.0
        assert data["heures_reelles"] == 50.0
        assert data["commentaire"] == "Updated comment"

    def test_update_project_not_found(self, client: TestClient):
        """Test updating a non-existent project returns 404."""
        # Act
        response = client.put(
            "/api/projects/99999",
            json={"nom": "New Name"}
        )

        # Assert
        assert response.status_code == 404
        assert "99999" in response.json()["detail"]

    def test_update_project_duplicate_name_returns_409(self, client: TestClient, unique_name: str):
        """Test updating to an existing name returns 409 Conflict."""
        # Arrange: Create two projects
        today = date.today()
        name_a = f"{unique_name}-A"
        name_b = f"{unique_name}-B"

        client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-UPD-DUP-A-{uuid.uuid4().hex[:8]}",
                "nom": name_a,
                "description": "First project",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
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
        )

        create_response = client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-UPD-DUP-B-{uuid.uuid4().hex[:8]}",
                "nom": name_b,
                "description": "Second project",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
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
        )
        project_b_id = create_response.json()["id"]

        # Act: Try to rename Project B to Project A (conflict)
        response = client.put(
            f"/api/projects/{project_b_id}",
            json={"nom": name_a}
        )

        # Assert
        assert response.status_code == 409
        assert name_a in response.json()["detail"]

    def test_update_project_invalid_heures_returns_422(self, client: TestClient, unique_name: str):
        """Test updating with invalid heures_planifiees returns 422."""
        # Arrange: Create a project
        today = date.today()
        name = f"{unique_name}-heures"

        create_response = client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-UPD-HEURES-{uuid.uuid4().hex[:8]}",
                "nom": name,
                "description": "Test",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
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
        )
        project_id = create_response.json()["id"]

        # Act: Try to update with negative heures_planifiees
        response = client.put(
            f"/api/projects/{project_id}",
            json={"heures_planifiees": -100.0}
        )

        # Assert
        assert response.status_code == 422


class TestDeleteProjectEndpoint:
    """Test suite for DELETE /api/projects/{id} endpoint."""

    def test_delete_project_success(self, client: TestClient):
        """Test successfully deleting a project."""
        # Arrange: Create a project
        today = date.today()
        create_response = client.post(
            "/api/projects",
            json={
                "numero": f"PROJ-DEL-{uuid.uuid4().hex[:8]}",
                "nom": "Project to Delete",
                "description": "Will be deleted",
                "date_debut": str(today),
                "date_echeance": str(today + timedelta(days=365)),
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
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Act: Delete the project
        delete_response = client.delete(f"/api/projects/{project_id}")

        # Assert: 204 No Content
        assert delete_response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404

    def test_delete_project_not_found(self, client: TestClient):
        """Test deleting a non-existent project returns 404."""
        # Act
        response = client.delete("/api/projects/99999")

        # Assert
        assert response.status_code == 404
        assert "99999" in response.json()["detail"]


class TestListProjectsEndpoint:
    """Test suite for GET /api/projects endpoint (list with pagination)."""

    def test_list_projects_empty(self, client: TestClient):
        """Test listing projects - may not be empty due to other tests."""
        # Act
        response = client.get("/api/projects")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)  # Should be a list (may be empty or not)

    def test_list_projects_returns_all_projects(self, client: TestClient, unique_name: str):
        """Test listing all projects."""
        # Arrange: Get current count first
        initial_response = client.get("/api/projects")
        initial_count = len(initial_response.json())

        # Create 3 projects with unique names
        today = date.today()
        created_names = []
        for i in range(3):
            name = f"{unique_name}-list-{i+1}"
            created_names.append(name)
            response = client.post(
                "/api/projects",
                json={
                    "numero": f"PROJ-LIST-{uuid.uuid4().hex[:8]}",
                    "nom": name,
                    "description": f"Description {i+1}",
                    "date_debut": str(today),
                    "date_echeance": str(today + timedelta(days=365)),
                    "type": "INTERNE",
                    "stade": "En cours",
                    "commentaire": None,
                    "heures_planifiees": 100.0 * (i + 1),
                    "heures_reelles": 0.0,
                    "est_template": False,
                    "projet_template_id": None,
                    "responsable_id": 1,
                    "entreprise_id": 1,
                    "contact_id": None
                }
            )
            assert response.status_code == 201

        # Act: Get all projects (with high limit to ensure we get our new ones)
        response = client.get("/api/projects?limit=100")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= initial_count + 3  # At least the initial + 3 we created
        # Check that our created projects are in the list
        response_names = [p["nom"] for p in data]
        for name in created_names:
            assert name in response_names

    def test_list_projects_pagination_limit(self, client: TestClient, unique_name: str):
        """Test pagination with limit parameter."""
        # Arrange: Create 5 projects with unique names
        today = date.today()
        for i in range(5):
            response = client.post(
                "/api/projects",
                json={
                    "numero": f"PROJ-LIMIT-{uuid.uuid4().hex[:8]}",
                    "nom": f"{unique_name}-limit-{i+1}",
                    "description": f"Description {i+1}",
                    "date_debut": str(today),
                    "date_echeance": str(today + timedelta(days=365)),
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
            )
            assert response.status_code == 201

        # Act: Request only 2 projects
        response = client.get("/api/projects?limit=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should limit to 2

    def test_list_projects_pagination_offset(self, client: TestClient, unique_name: str):
        """Test pagination with offset parameter."""
        # Arrange: Get current count
        initial_response = client.get("/api/projects")
        initial_count = len(initial_response.json())

        # Create 3 new projects with unique names
        today = date.today()
        for i in range(3):
            response = client.post(
                "/api/projects",
                json={
                    "numero": f"PROJ-OFFSET-{uuid.uuid4().hex[:8]}",
                    "nom": f"{unique_name}-offset-{i+1}",
                    "description": f"Description {i+1}",
                    "date_debut": str(today),
                    "date_echeance": str(today + timedelta(days=365)),
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
            )
            assert response.status_code == 201

        # Act: Skip first N projects
        response = client.get(f"/api/projects?offset={initial_count + 2}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1  # Should get at least the last project we created

    def test_list_projects_pagination_offset_and_limit(self, client: TestClient, unique_name: str):
        """Test pagination with both offset and limit."""
        # Arrange: Get current count
        initial_response = client.get("/api/projects")
        initial_count = len(initial_response.json())

        # Create 5 projects with unique names
        today = date.today()
        created_names = []
        for i in range(5):
            name = f"{unique_name}-both-{i+1}"
            created_names.append(name)
            response = client.post(
                "/api/projects",
                json={
                    "numero": f"PROJ-BOTH-{uuid.uuid4().hex[:8]}",
                    "nom": name,
                    "description": f"Description {i+1}",
                    "date_debut": str(today),
                    "date_echeance": str(today + timedelta(days=365)),
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
            )
            assert response.status_code == 201

        # Act: Skip first (initial_count + 1), get 2
        response = client.get(f"/api/projects?offset={initial_count + 1}&limit=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should get exactly 2 projects
