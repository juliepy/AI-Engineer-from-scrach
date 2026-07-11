"""Tests for contacts endpoints.

Note: contacts still use legacy session-token auth (intentional smell).
"""
from fastapi.testclient import TestClient

from app.models import Contact


class TestListContacts:
    def test_list_requires_session_token(self, client: TestClient) -> None:
        resp = client.get("/api/contacts")
        assert resp.status_code == 401

    def test_jwt_rejected_on_contacts(
        self, client: TestClient, admin_headers: dict
    ) -> None:
        """Contacts use legacy auth, not JWT — demonstrates the mixed-auth smell."""
        resp = client.get("/api/contacts", headers=admin_headers)
        # JWT header is not the X-Session-Token; should get 401
        assert resp.status_code == 401

    def test_list_with_session_token(
        self, client: TestClient, admin_session_headers: dict, contact: Contact
    ) -> None:
        resp = client.get("/api/contacts", headers=admin_session_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_scoped_to_team(
        self,
        client: TestClient,
        admin_session_headers: dict,
        contact: Contact,
    ) -> None:
        resp = client.get("/api/contacts", headers=admin_session_headers)
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json()]
        assert contact.id in ids


class TestCreateContact:
    def test_create_contact(
        self, client: TestClient, admin_session_headers: dict
    ) -> None:
        resp = client.post(
            "/api/contacts",
            json={
                "name": "New Contact",
                "email": "new@example.test",
                "company": "TestCo",
                "stage": "lead",
            },
            headers=admin_session_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New Contact"
        assert data["stage"] == "lead"

    def test_create_with_all_fields(
        self, client: TestClient, admin_session_headers: dict
    ) -> None:
        resp = client.post(
            "/api/contacts",
            json={
                "name": "Full Contact",
                "email": "full@example.test",
                "company": "FullCo",
                "phone": "+1-555-0123",
                "title": "VP Sales",
                "notes": "Met at conf",
                "stage": "opportunity",
            },
            headers=admin_session_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] == "+1-555-0123"
        assert data["title"] == "VP Sales"


class TestGetContact:
    def test_get_contact(
        self, client: TestClient, admin_session_headers: dict, contact: Contact
    ) -> None:
        resp = client.get(f"/api/contacts/{contact.id}", headers=admin_session_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == contact.id

    def test_get_not_found(
        self, client: TestClient, admin_session_headers: dict
    ) -> None:
        resp = client.get("/api/contacts/99999", headers=admin_session_headers)
        assert resp.status_code == 404


class TestUpdateContact:
    def test_update_stage(
        self, client: TestClient, admin_session_headers: dict, contact: Contact
    ) -> None:
        resp = client.patch(
            f"/api/contacts/{contact.id}",
            json={"stage": "customer"},
            headers=admin_session_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["stage"] == "customer"

    def test_update_name_and_email(
        self, client: TestClient, admin_session_headers: dict, contact: Contact
    ) -> None:
        resp = client.patch(
            f"/api/contacts/{contact.id}",
            json={"name": "Updated Name", "email": "updated@example.test"},
            headers=admin_session_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.test"


class TestDeleteContact:
    def test_delete_contact(
        self, client: TestClient, admin_session_headers: dict, contact: Contact
    ) -> None:
        resp = client.delete(f"/api/contacts/{contact.id}", headers=admin_session_headers)
        assert resp.status_code == 204
        # Verify gone
        resp2 = client.get(f"/api/contacts/{contact.id}", headers=admin_session_headers)
        assert resp2.status_code == 404
