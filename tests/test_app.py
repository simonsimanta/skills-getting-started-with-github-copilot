import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Deep-copy activities state before each test and restore after."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


@pytest.fixture
def client():
    return TestClient(app)


# GET /activities

def test_get_activities_returns_200(client):
    assert client.get("/activities").status_code == 200


def test_get_activities_returns_dict(client):
    data = client.get("/activities").json()
    assert isinstance(data, dict) and len(data) > 0


def test_get_activities_required_keys(client):
    for details in client.get("/activities").json().values():
        assert {"description", "schedule", "max_participants", "participants"} <= details.keys()


# POST /activities/{activity_name}/signup

def test_signup_success(client):
    r = client.post("/activities/Chess Club/signup", params={"email": "new@mergington.edu"})
    assert r.status_code == 200
    assert "new@mergington.edu" in r.json()["message"]
    assert "Chess Club" in r.json()["message"]


def test_signup_unknown_activity(client):
    r = client.post("/activities/Unknown Activity/signup", params={"email": "x@mergington.edu"})
    assert r.status_code == 404


def test_signup_duplicate(client):
    # michael@mergington.edu is already in Chess Club
    r = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert r.status_code == 400


# DELETE /activities/{activity_name}/unregister

def test_unregister_success(client):
    r = client.delete("/activities/Chess Club/unregister", params={"email": "michael@mergington.edu"})
    assert r.status_code == 200
    assert "michael@mergington.edu" in r.json()["message"]
    assert "Chess Club" in r.json()["message"]


def test_unregister_unknown_activity(client):
    r = client.delete("/activities/Unknown Activity/unregister", params={"email": "x@mergington.edu"})
    assert r.status_code == 404


def test_unregister_not_a_participant(client):
    r = client.delete("/activities/Chess Club/unregister", params={"email": "nothere@mergington.edu"})
    assert r.status_code == 404
