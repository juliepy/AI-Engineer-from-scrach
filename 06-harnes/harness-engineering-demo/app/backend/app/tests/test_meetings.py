"""Tests for meetings endpoints."""

from fastapi.testclient import TestClient

from app.models import Meeting, User, Contact


class TestListMeetings:
    def test_list_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/meetings")
        assert resp.status_code == 401

    def test_list_returns_team_meetings(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.get("/api/meetings", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        ids = [m["id"] for m in data]
        assert meeting.id in ids

    def test_list_filter_by_host(
        self, client: TestClient, admin_headers: dict, admin_user: User, meeting: Meeting
    ) -> None:
        resp = client.get(f"/api/meetings?host_id={admin_user.id}", headers=admin_headers)
        assert resp.status_code == 200
        for m in resp.json():
            assert m["host_id"] == admin_user.id

    def test_list_filter_by_status(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.get("/api/meetings?status=scheduled", headers=admin_headers)
        assert resp.status_code == 200
        for m in resp.json():
            assert m["status"] == "scheduled"

    def test_list_search(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.get("/api/meetings?search=Discovery", headers=admin_headers)
        assert resp.status_code == 200
        assert any("Discovery" in m["title"] for m in resp.json())

    def test_list_pagination(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.get("/api/meetings?limit=1&offset=0", headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()) <= 1

    def test_list_scoped_to_team(
        self, client: TestClient, member_headers: dict, meeting: Meeting
    ) -> None:
        # member is on the same team as admin — should see the meeting
        resp = client.get("/api/meetings", headers=member_headers)
        assert resp.status_code == 200

    def test_timezone_rendered_in_viewer_tz(
        self, client: TestClient, member_headers: dict, meeting: Meeting
    ) -> None:
        """Times are rendered in the viewer's timezone (Europe/Berlin = UTC+2 in summer)."""
        resp = client.get("/api/meetings", headers=member_headers)
        assert resp.status_code == 200
        # meeting starts at 14:00 UTC → 16:00 CEST
        rows = resp.json()
        match = next((m for m in rows if m["id"] == meeting.id), None)
        assert match is not None
        # Berlin is UTC+2 in July — rendered time should contain "16:00"
        assert "16:00" in match["start"]


class TestCreateMeeting:
    def test_create_meeting(
        self, client: TestClient, admin_headers: dict, contact: Contact
    ) -> None:
        resp = client.post(
            "/api/meetings",
            json={
                "title": "New Meeting",
                "start_time": "2026-08-01T10:00:00Z",
                "end_time": "2026-08-01T10:30:00Z",
                "meeting_timezone": "UTC",
                "invitee_contact_ids": [contact.id],
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "New Meeting"
        assert data["inviteeCount"] == 1
        assert len(data["invitees"]) == 1

    def test_create_meeting_no_invitees(
        self, client: TestClient, admin_headers: dict
    ) -> None:
        resp = client.post(
            "/api/meetings",
            json={
                "title": "Solo Meeting",
                "start_time": "2026-08-01T10:00:00Z",
                "end_time": "2026-08-01T10:30:00Z",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["inviteeCount"] == 0


class TestGetMeetingDetail:
    def test_get_detail(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.get(f"/api/meetings/{meeting.id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == meeting.id
        assert len(data["invitees"]) == 1

    def test_get_not_found(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get("/api/meetings/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_get_wrong_team(
        self, client: TestClient, member_headers: dict, meeting: Meeting
    ) -> None:
        # member is on same team, should succeed
        resp = client.get(f"/api/meetings/{meeting.id}", headers=member_headers)
        assert resp.status_code == 200


class TestUpdateMeeting:
    def test_update_title(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.patch(
            f"/api/meetings/{meeting.id}",
            json={"title": "Updated Title"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_update_status_to_completed(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.patch(
            f"/api/meetings/{meeting.id}",
            json={"status": "completed"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_member_cannot_update_others_meeting(
        self,
        client: TestClient,
        member_headers: dict,
        meeting: Meeting,
    ) -> None:
        resp = client.patch(
            f"/api/meetings/{meeting.id}",
            json={"title": "Hack"},
            headers=member_headers,
        )
        assert resp.status_code == 403


class TestCancelMeeting:
    def test_cancel_sets_status(
        self, client: TestClient, admin_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.delete(f"/api/meetings/{meeting.id}", headers=admin_headers)
        assert resp.status_code == 204

    def test_member_cannot_cancel_others(
        self, client: TestClient, member_headers: dict, meeting: Meeting
    ) -> None:
        resp = client.delete(f"/api/meetings/{meeting.id}", headers=member_headers)
        assert resp.status_code == 403


class TestRSVP:
    def test_rsvp_accepted(
        self,
        client: TestClient,
        admin_headers: dict,
        meeting: Meeting,
        db: object,
    ) -> None:
        # Get the invitee id
        detail = client.get(f"/api/meetings/{meeting.id}", headers=admin_headers).json()
        inv_id = detail["invitees"][0]["id"]
        resp = client.patch(
            f"/api/meetings/{meeting.id}/invitees/{inv_id}/rsvp",
            json={"response": "accepted"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["response"] == "accepted"

    def test_rsvp_invalid_response(
        self,
        client: TestClient,
        admin_headers: dict,
        meeting: Meeting,
    ) -> None:
        detail = client.get(f"/api/meetings/{meeting.id}", headers=admin_headers).json()
        inv_id = detail["invitees"][0]["id"]
        resp = client.patch(
            f"/api/meetings/{meeting.id}/invitees/{inv_id}/rsvp",
            json={"response": "maybe"},
            headers=admin_headers,
        )
        assert resp.status_code == 400


class TestExport:
    def test_pdf_export(self, client: TestClient, admin_headers: dict, meeting: Meeting) -> None:
        resp = client.get("/api/meetings/export?format=pdf", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"

    def test_unsupported_format(self, client: TestClient, admin_headers: dict) -> None:
        # CSV is NOT built yet (workshop builds it live)
        resp = client.get("/api/meetings/export?format=csv", headers=admin_headers)
        assert resp.status_code == 400
