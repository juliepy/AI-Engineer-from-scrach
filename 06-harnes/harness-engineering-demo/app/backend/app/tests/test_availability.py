"""Tests for availability CRUD endpoints."""
from fastapi.testclient import TestClient

from app.models import AvailabilitySlot, User


class TestGetAvailability:
    def test_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/availability")
        assert resp.status_code == 401

    def test_get_own_availability(
        self, client: TestClient, admin_headers: dict, availability_slot: AvailabilitySlot
    ) -> None:
        resp = client.get("/api/availability", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        ids = [s["id"] for s in data]
        assert availability_slot.id in ids

    def test_get_other_user_availability(
        self,
        client: TestClient,
        member_headers: dict,
        admin_user: User,
        availability_slot: AvailabilitySlot,
    ) -> None:
        resp = client.get(f"/api/availability/user/{admin_user.id}", headers=member_headers)
        assert resp.status_code == 200
        ids = [s["id"] for s in resp.json()]
        assert availability_slot.id in ids

    def test_get_unknown_user_availability(
        self, client: TestClient, admin_headers: dict
    ) -> None:
        resp = client.get("/api/availability/user/99999", headers=admin_headers)
        assert resp.status_code == 404


class TestAddSlot:
    def test_add_slot(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            "/api/availability",
            json={"weekday": 1, "start": "10:00", "end": "18:00"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["weekday"] == 1
        assert data["start"] == "10:00"
        assert data["end"] == "18:00"


class TestBulkSetAvailability:
    def test_bulk_set_replaces_all(
        self, client: TestClient, admin_headers: dict, availability_slot: AvailabilitySlot
    ) -> None:
        resp = client.put(
            "/api/availability",
            json={
                "slots": [
                    {"weekday": 0, "start": "08:00", "end": "16:00"},
                    {"weekday": 1, "start": "08:00", "end": "16:00"},
                    {"weekday": 2, "start": "08:00", "end": "16:00"},
                ]
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        for s in data:
            assert s["start"] == "08:00"

    def test_bulk_set_clears_all(
        self, client: TestClient, admin_headers: dict, availability_slot: AvailabilitySlot
    ) -> None:
        resp = client.put(
            "/api/availability",
            json={"slots": []},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []


class TestDeleteSlot:
    def test_delete_slot(
        self, client: TestClient, admin_headers: dict, availability_slot: AvailabilitySlot
    ) -> None:
        resp = client.delete(
            f"/api/availability/{availability_slot.id}", headers=admin_headers
        )
        assert resp.status_code == 204

    def test_delete_not_found(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.delete("/api/availability/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_cannot_delete_other_users_slot(
        self,
        client: TestClient,
        member_headers: dict,
        availability_slot: AvailabilitySlot,
    ) -> None:
        # availability_slot belongs to admin_user, not member_user
        resp = client.delete(
            f"/api/availability/{availability_slot.id}", headers=member_headers
        )
        assert resp.status_code == 404
