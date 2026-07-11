"""Tests for teams endpoints."""
from fastapi.testclient import TestClient

from app.models import User, Team


class TestGetTeam:
    def test_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/teams/me")
        assert resp.status_code == 401

    def test_get_team(
        self, client: TestClient, admin_headers: dict, team: Team, admin_user: User
    ) -> None:
        resp = client.get("/api/teams/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == team.id
        assert data["name"] == "Test Team"
        assert len(data["members"]) >= 1

    def test_members_include_admin(
        self, client: TestClient, admin_headers: dict, admin_user: User
    ) -> None:
        resp = client.get("/api/teams/me", headers=admin_headers)
        assert resp.status_code == 200
        emails = [m["email"] for m in resp.json()["members"]]
        assert admin_user.email in emails


class TestInviteMember:
    def test_admin_can_invite(
        self, client: TestClient, admin_headers: dict
    ) -> None:
        resp = client.post(
            "/api/teams/me/members",
            json={
                "email": "newmember@test.test",
                "full_name": "New Member",
                "role": "member",
                "timezone": "UTC",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newmember@test.test"
        assert data["role"] == "member"

    def test_member_cannot_invite(
        self, client: TestClient, member_headers: dict
    ) -> None:
        resp = client.post(
            "/api/teams/me/members",
            json={
                "email": "another@test.test",
                "full_name": "Another",
                "role": "member",
            },
            headers=member_headers,
        )
        assert resp.status_code == 403

    def test_duplicate_email_rejected(
        self, client: TestClient, admin_headers: dict, member_user: User
    ) -> None:
        resp = client.post(
            "/api/teams/me/members",
            json={
                "email": member_user.email,
                "full_name": "Dup",
                "role": "member",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 409


class TestUpdateMemberRole:
    def test_admin_can_change_role(
        self, client: TestClient, admin_headers: dict, member_user: User
    ) -> None:
        resp = client.patch(
            f"/api/teams/me/members/{member_user.id}/role",
            json={"role": "admin"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_invalid_role_rejected(
        self, client: TestClient, admin_headers: dict, member_user: User
    ) -> None:
        resp = client.patch(
            f"/api/teams/me/members/{member_user.id}/role",
            json={"role": "superuser"},
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_member_cannot_change_role(
        self, client: TestClient, member_headers: dict, admin_user: User
    ) -> None:
        resp = client.patch(
            f"/api/teams/me/members/{admin_user.id}/role",
            json={"role": "member"},
            headers=member_headers,
        )
        assert resp.status_code == 403


class TestRemoveMember:
    def test_admin_can_remove(
        self, client: TestClient, admin_headers: dict, member_user: User
    ) -> None:
        resp = client.delete(
            f"/api/teams/me/members/{member_user.id}", headers=admin_headers
        )
        assert resp.status_code == 204

    def test_cannot_remove_self(
        self, client: TestClient, admin_headers: dict, admin_user: User
    ) -> None:
        resp = client.delete(
            f"/api/teams/me/members/{admin_user.id}", headers=admin_headers
        )
        assert resp.status_code == 400

    def test_member_cannot_remove(
        self, client: TestClient, member_headers: dict, admin_user: User
    ) -> None:
        resp = client.delete(
            f"/api/teams/me/members/{admin_user.id}", headers=member_headers
        )
        assert resp.status_code == 403
