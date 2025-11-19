"""API endpoint tests."""

from uuid import uuid4

import pytest


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "securepassword123",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123"},  # Same as test_user
        )
        assert response.status_code == 400

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401


class TestProjectEndpoints:
    """Test project management endpoints."""

    def test_create_project(self, client, auth_headers):
        """Test project creation."""
        response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "A test project"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert "id" in data

    def test_list_projects(self, client, auth_headers):
        """Test listing projects."""
        # Create a project first
        client.post("/api/v1/projects", json={"name": "Project 1"}, headers=auth_headers)

        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_project(self, client, auth_headers):
        """Test getting single project."""
        # Create project
        create_response = client.post("/api/v1/projects", json={"name": "Test Project"}, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Get project
        response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Project"

    def test_get_nonexistent_project(self, client, auth_headers):
        """Test getting nonexistent project returns 404."""
        response = client.get(f"/api/v1/projects/{uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    def test_update_project(self, client, auth_headers):
        """Test updating project."""
        # Create project
        create_response = client.post("/api/v1/projects", json={"name": "Original Name"}, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Update project
        response = client.put(
            f"/api/v1/projects/{project_id}", json={"name": "Updated Name"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_project(self, client, auth_headers):
        """Test deleting (archiving) project."""
        # Create project
        create_response = client.post("/api/v1/projects", json={"name": "To Delete"}, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200

    def test_unauthorized_access(self, client):
        """Test endpoints require authentication."""
        response = client.get("/api/v1/projects")
        assert response.status_code in [401, 403]


class TestFittingEndpoints:
    """Test fitting management endpoints."""

    def test_create_fitting(self, client, auth_headers):
        """Test creating fitting in project."""
        # Create project first
        project_response = client.post("/api/v1/projects", json={"name": "Fitting Project"}, headers=auth_headers)
        project_id = project_response.json()["id"]

        # Create fitting
        response = client.post(
            f"/api/v1/fittings/project/{project_id}", json={"name": "fit-d300"}, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "fit-d300"
        assert data["status"] == "PENDING"

    def test_list_fittings(self, client, auth_headers):
        """Test listing fittings in project."""
        # Create project
        project_response = client.post("/api/v1/projects", json={"name": "Fitting Project"}, headers=auth_headers)
        project_id = project_response.json()["id"]

        # Create fitting
        client.post(f"/api/v1/fittings/project/{project_id}", json={"name": "fit-1"}, headers=auth_headers)

        # List fittings
        response = client.get(f"/api/v1/fittings/project/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_fitting(self, client, auth_headers):
        """Test getting single fitting."""
        # Create project and fitting
        project_response = client.post("/api/v1/projects", json={"name": "Test Project"}, headers=auth_headers)
        project_id = project_response.json()["id"]

        fitting_response = client.post(
            f"/api/v1/fittings/project/{project_id}", json={"name": "test-fit"}, headers=auth_headers
        )
        fitting_id = fitting_response.json()["id"]

        # Get fitting
        response = client.get(f"/api/v1/fittings/{fitting_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "test-fit"


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
