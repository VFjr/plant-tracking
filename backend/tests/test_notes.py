from fastapi.testclient import TestClient


def test_list_notes_empty(client: TestClient, plant: dict) -> None:
    response = client.get(f"/api/plants/{plant['id']}/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_notes(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/notes",
        json={"content": "Roots looking healthy"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Roots looking healthy"
    assert data["plant_id"] == plant["id"]

    response = client.get(f"/api/plants/{plant['id']}/notes")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_note_empty_content_rejected(client: TestClient, plant: dict) -> None:
    response = client.post(f"/api/plants/{plant['id']}/notes", json={"content": ""})
    assert response.status_code == 422


def test_create_note_missing_plant(client: TestClient) -> None:
    response = client.post("/api/plants/999/notes", json={"content": "Ghost note"})
    assert response.status_code == 404


def test_delete_note(client: TestClient, plant: dict) -> None:
    create_response = client.post(
        f"/api/plants/{plant['id']}/notes",
        json={"content": "Temporary note"},
    )
    note_id = create_response.json()["id"]

    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 204

    response = client.get(f"/api/plants/{plant['id']}/notes")
    assert response.json() == []


def test_delete_missing_note(client: TestClient) -> None:
    response = client.delete("/api/notes/999")
    assert response.status_code == 404
