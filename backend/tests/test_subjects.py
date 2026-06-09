"""Tests for subjects and materials API."""

from io import BytesIO

from fastapi.testclient import TestClient


class TestSubjectsAPI:
    def test_create_and_list_subjects(self, client: TestClient):
        create_response = client.post(
            "/api/subjects/",
            json={"name": "Biology", "description": "Cell biology and genetics"},
        )
        assert create_response.status_code == 201
        subject = create_response.json()
        assert subject["name"] == "Biology"
        assert subject["material_count"] == 0

        list_response = client.get("/api/subjects/")
        assert list_response.status_code == 200
        subjects = list_response.json()["subjects"]
        assert len(subjects) == 1
        assert subjects[0]["id"] == subject["id"]

    def test_update_and_delete_subject(self, client: TestClient):
        create_response = client.post("/api/subjects/", json={"name": "Physics"})
        subject_id = create_response.json()["id"]

        update_response = client.patch(
            f"/api/subjects/{subject_id}",
            json={"name": "Advanced Physics"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Advanced Physics"

        delete_response = client.delete(f"/api/subjects/{subject_id}")
        assert delete_response.status_code == 204

        list_response = client.get("/api/subjects/")
        assert list_response.json()["subjects"] == []

    def test_upload_material(self, client: TestClient):
        create_response = client.post("/api/subjects/", json={"name": "Chemistry"})
        subject_id = create_response.json()["id"]

        upload_response = client.post(
            f"/api/subjects/{subject_id}/materials",
            data={"material_kind": "notes"},
            files={"file": ("notes.txt", BytesIO(b"Atoms combine to form molecules."), "text/plain")},
        )
        assert upload_response.status_code == 201
        material = upload_response.json()
        assert material["filename"] == "notes.txt"
        assert material["status"] in {"pending", "processing", "ready", "failed"}

        list_response = client.get(f"/api/subjects/{subject_id}/materials")
        assert list_response.status_code == 200
        assert len(list_response.json()["materials"]) == 1

    def test_search_requires_subject(self, client: TestClient):
        response = client.post(
            "/api/subjects/missing-id/search",
            json={"query": "photosynthesis"},
        )
        assert response.status_code == 404
