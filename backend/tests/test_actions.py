from fastapi.testclient import TestClient


def test_list_actions_empty(client: TestClient, plant: dict) -> None:
    response = client.get(f"/api/plants/{plant['id']}/actions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_actions(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={
            "action_type": "flush",
            "performed_at": "2026-07-01",
            "notes": "Ran tap water through",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["action_type"] == "flush"
    assert data["performed_at"] == "2026-07-01"
    assert data["notes"] == "Ran tap water through"

    response = client.get(f"/api/plants/{plant['id']}/actions")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_action_missing_plant(client: TestClient) -> None:
    response = client.post(
        "/api/plants/999/actions",
        json={"action_type": "other", "performed_at": "2026-07-01"},
    )
    assert response.status_code == 404


def test_delete_action(client: TestClient, plant: dict) -> None:
    create_response = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "reservoir_refill", "performed_at": "2026-07-02"},
    )
    action_id = create_response.json()["id"]

    response = client.delete(f"/api/actions/{action_id}")
    assert response.status_code == 204

    response = client.get(f"/api/plants/{plant['id']}/actions")
    assert response.json() == []


def test_delete_missing_action(client: TestClient) -> None:
    response = client.delete("/api/actions/999")
    assert response.status_code == 404


def test_delete_plant_cascades_notes_and_actions(client: TestClient, plant: dict) -> None:
    client.post(f"/api/plants/{plant['id']}/notes", json={"content": "Note"})
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )

    response = client.delete(f"/api/plants/{plant['id']}")
    assert response.status_code == 204


def test_cutting_rejects_flush_action(client: TestClient, cutting: dict) -> None:
    response = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )
    assert response.status_code == 422


def test_cutting_rejects_reservoir_refill_action(client: TestClient, cutting: dict) -> None:
    response = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "reservoir_refill", "performed_at": "2026-07-01"},
    )
    assert response.status_code == 422


def test_semi_hydro_rejects_monitor_action(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    assert response.status_code == 422


def test_semi_hydro_rejects_water_change_action(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "water_change", "performed_at": "2026-07-01"},
    )
    assert response.status_code == 422


def test_cutting_allows_monitor_and_water_change_actions(client: TestClient, cutting: dict) -> None:
    monitor = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    water_change = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "water_change", "performed_at": "2026-07-02"},
    )
    assert monitor.status_code == 201
    assert water_change.status_code == 201
