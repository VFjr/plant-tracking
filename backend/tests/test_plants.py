from fastapi.testclient import TestClient


def test_create_and_get_plant(client: TestClient) -> None:
    response = client.post(
        "/api/plants",
        json={
            "name": "Monstera",
            "species": "Monstera deliciosa",
            "location": "Living room",
            "description": "LECA in glass jar, 50% strength fertilizer",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Monstera"
    assert data["species"] == "Monstera deliciosa"
    assert data["location"] == "Living room"
    assert data["description"] == "LECA in glass jar, 50% strength fertilizer"
    assert data["kind"] == "semi_hydro"
    assert data["monitor_interval_days"] is None
    assert data["next_monitor_date"] is None
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


def test_create_cutting_defaults_kind(client: TestClient) -> None:
    response = client.post(
        "/api/plants",
        json={"name": "Pothos cutting", "kind": "cutting", "description": "In glass jar"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["kind"] == "cutting"
    assert data["flush_interval_days"] is None
    assert data["next_flush_date"] is None
    assert data["monitor_interval_days"] is None
    assert data["next_monitor_date"] is None


def test_create_plant_defaults_to_semi_hydro(client: TestClient) -> None:
    response = client.post("/api/plants", json={"name": "Monstera"})
    assert response.status_code == 201
    assert response.json()["kind"] == "semi_hydro"


def test_update_plant_does_not_change_kind(client: TestClient) -> None:
    create_response = client.post("/api/plants", json={"name": "Cutting", "kind": "cutting"})
    plant_id = create_response.json()["id"]

    response = client.patch(f"/api/plants/{plant_id}", json={"name": "Renamed Cutting"})
    assert response.status_code == 200
    assert response.json()["kind"] == "cutting"
