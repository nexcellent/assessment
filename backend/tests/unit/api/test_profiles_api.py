"""The HTTP surface: routing, response shapes and the central error mapping, on the fixture store."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.utils.profile_factory import FIXTURES_DIR

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_health_reports_the_profile_store(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["services"]["profile_store"]["connected"] is True


def test_list_and_get(client: TestClient) -> None:
    listed = client.get("/api/v1/profiles").json()
    assert listed["count"] == listed["total_count"] == len(list(FIXTURES_DIR.glob("*.json")))

    response = client.get(f"/api/v1/profiles/{listed['profiles'][0]['id']}")

    assert response.status_code == 200
    assert response.json()["profile"]["id"] == listed["profiles"][0]["id"]


def test_an_unknown_profile_answers_404_with_the_domain_code(client: TestClient) -> None:
    response = client.get("/api/v1/profiles/nobody")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROFILE_NOT_FOUND"


def test_an_entry_with_empty_mandatory_fields_answers_422(client: TestClient) -> None:
    response = client.put("/api/v1/profiles/lena-hoffmann/projects/proj-1", json={"title": "Only a title"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "MANDATORY_FIELDS_MISSING"


def test_a_complete_entry_replaces_the_stored_one(client: TestClient) -> None:
    entry = {"title": "Renamed Project", "role": "Lead", "start_date": "2024-09-01", "end_date": "2026-06-30"}

    response = client.put("/api/v1/profiles/lena-hoffmann/projects/proj-6", json=entry)

    assert response.status_code == 200
    projects = client.get("/api/v1/profiles/lena-hoffmann").json()["profile"]["projects"]
    assert projects[0]["title"] == "Renamed Project" and projects[0]["duration_months"] == 22
