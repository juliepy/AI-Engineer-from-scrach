"""Tests for authentication — both JWT and legacy session token."""
from fastapi.testclient import TestClient

from app.models import User


class TestJWTLogin:
    def test_login_success(self, client: TestClient, admin_user: User) -> None:
        resp = client.post(
            "/api/auth/login",
            data={"username": "admin@test.test", "password": "password123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, admin_user: User) -> None:
        resp = client.post(
            "/api/auth/login",
            data={"username": "admin@test.test", "password": "wrongpass"},
        )
        assert resp.status_code == 400

    def test_login_unknown_user(self, client: TestClient) -> None:
        resp = client.post(
            "/api/auth/login",
            data={"username": "nobody@test.test", "password": "password123"},
        )
        assert resp.status_code == 400

    def test_me_returns_user(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get("/api/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@test.test"
        assert data["role"] == "admin"

    def test_me_unauthorized(self, client: TestClient) -> None:
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_bad_token(self, client: TestClient) -> None:
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer bad_token"})
        assert resp.status_code == 401


class TestLegacyLogin:
    def test_legacy_login_success(self, client: TestClient, admin_user: User) -> None:
        resp = client.post(
            "/api/auth/legacy-login",
            data={"username": "admin@test.test", "password": "password123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_token" in data

    def test_legacy_login_wrong_password(self, client: TestClient, admin_user: User) -> None:
        resp = client.post(
            "/api/auth/legacy-login",
            data={"username": "admin@test.test", "password": "wrong"},
        )
        assert resp.status_code == 400


class TestProfileUpdate:
    def test_update_profile(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.patch(
            "/api/auth/me/profile",
            json={"full_name": "Updated Name", "timezone": "America/Chicago"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Updated Name"
        assert data["timezone"] == "America/Chicago"

    def test_change_password(self, client: TestClient, admin_user: User, admin_headers: dict) -> None:
        resp = client.post(
            "/api/auth/me/change-password",
            json={"current_password": "password123", "new_password": "newpass456"},
            headers=admin_headers,
        )
        assert resp.status_code == 204

    def test_change_password_wrong_current(
        self, client: TestClient, admin_user: User, admin_headers: dict
    ) -> None:
        resp = client.post(
            "/api/auth/me/change-password",
            json={"current_password": "wrongpass", "new_password": "newpass456"},
            headers=admin_headers,
        )
        assert resp.status_code == 400
