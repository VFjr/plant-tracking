from fastapi.testclient import TestClient


def test_create_and_get_plant(client: TestClient) -> None:
    response = client.post(
        "/api/plants",
        json={"name": "Monstera", "species": "Monstera deliciosa", "location": "Living room"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Monstera"
    assert data["species"] == "Monstera deliciosa"
    assert data["location"] == "Living room"
    assert "id" in data

    plant_id = data["id"]
    response = client.get(f"/api/plants/{plant_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Monstera"


def test_list_plants(client: TestClient) -> None:
    client.post("/api/plants", json={"name": "Pothos"})
    client.post("/api/plants", json={"name": "Monstera"})

    response = client.get("/api/plants")
    assert response.status_code == 200
    names = [plant["name"] for plant in response.json()]
    assert names == ["Monstera", "Pothos"]


def test_update_plant(client: TestClient) -> None:
    create_response = client.post("/api/plants", json={"name": "Pothos"})
    plant_id = create_response.json()["id"]

    response = client.patch(f"/api/plants/{plant_id}", json={"location": "Kitchen"})
    assert response.status_code == 200
    assert response.json()["location"] == "Kitchen"
    assert response.json()["name"] == "Pothos"


def test_delete_plant(client: TestClient) -> None:
    create_response = client.post("/api/plants", json={"name": "Pothos"})
    plant_id = create_response.json()["id"]

    response = client.delete(f"/api/plants/{plant_id}")
    assert response.status_code == 204

    response = client.get(f"/api/plants/{plant_id}")
    assert response.status_code == 404


def test_get_missing_plant(client: TestClient) -> None:
    response = client.get("/api/plants/999")
    assert response.status_code == 404


def test_create_plant_empty_name_rejected(client: TestClient) -> None:
    response = client.post("/api/plants", json={"name": ""})
    assert response.status_code == 422


def test_create_plant_whitespace_name_rejected(client: TestClient) -> None:
    response = client.post("/api/plants", json={"name": "   "})
    assert response.status_code == 422


def test_update_plant_empty_name_rejected(client: TestClient) -> None:
    create_response = client.post("/api/plants", json={"name": "Pothos"})
    plant_id = create_response.json()["id"]

    response = client.patch(f"/api/plants/{plant_id}", json={"name": ""})
    assert response.status_code == 422


def test_patch_missing_plant(client: TestClient) -> None:
    response = client.patch("/api/plants/999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_missing_plant(client: TestClient) -> None:
    response = client.delete("/api/plants/999")
    assert response.status_code == 404
