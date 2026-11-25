import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["DATABASE"] = str(tmp_path / "test.db")

    init_db()

    with app.test_client() as client:
        yield client


def test_home(client):
    assert client.get("/").status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_create_note(client):
    response = client.post("/api/notes", json={
        "title": "Test Note",
        "content": "Testing QuickNote"
    })
    assert response.status_code == 201


def test_get_notes(client):
    client.post("/api/notes", json={
        "title": "Docker",
        "content": "Container testing"
    })

    response = client.get("/api/notes")

    assert response.status_code == 200
    assert len(response.json) == 1


def test_update_note(client):
    response = client.post("/api/notes", json={
        "title": "Old title",
        "content": "Old content"
    })

    note_id = response.json["id"]

    response = client.put(f"/api/notes/{note_id}", json={
        "title": "Updated title",
        "content": "Updated content"
    })

    assert response.status_code == 200
    assert client.get("/api/notes").json[0]["title"] == "Updated title"


def test_delete_note(client):
    response = client.post("/api/notes", json={
        "title": "Delete me",
        "content": "Temporary note"
    })

    note_id = response.json["id"]

    assert client.delete(
        f"/api/notes/{note_id}"
    ).status_code == 200

    assert client.get("/api/notes").json == []


def test_invalid_note(client):
    response = client.post("/api/notes", json={
        "title": "",
        "content": "Invalid note"
    })

    assert response.status_code == 400


def test_missing_note(client):
    assert client.delete("/api/notes/999").status_code == 404
