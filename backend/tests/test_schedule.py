from fastapi.testclient import TestClient


def test_set_schedule_computes_next_from_flush_action(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )

    response = client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["flush_interval_days"] == 7
    assert data["last_flush_date"] == "2026-07-01"
    assert data["next_flush_date"] == "2026-07-08"


def test_log_flush_advances_schedule(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    response = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-05"},
    )
    assert response.status_code == 201

    plant_response = client.get(f"/api/plants/{plant['id']}")
    data = plant_response.json()
    assert data["last_flush_date"] == "2026-07-05"
    assert data["next_flush_date"] == "2026-07-12"


def test_log_reservoir_refill_does_not_advance_schedule(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "reservoir_refill", "performed_at": "2026-07-05"},
    )

    plant_response = client.get(f"/api/plants/{plant['id']}")
    assert plant_response.json()["next_flush_date"] == "2026-07-08"


def test_log_flush_without_interval_does_not_set_next_date(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-05"},
    )

    plant_response = client.get(f"/api/plants/{plant['id']}")
    data = plant_response.json()
    assert data["next_flush_date"] is None
    assert data["last_flush_date"] == "2026-07-05"


def test_clear_flush_interval(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    response = client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": None},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["flush_interval_days"] is None
    assert data["next_flush_date"] is None


def test_schedule_without_flush_action_sets_no_next_date(client: TestClient, plant: dict) -> None:
    response = client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["flush_interval_days"] == 7
    assert data["last_flush_date"] is None
    assert data["next_flush_date"] is None


def test_schedule_missing_plant(client: TestClient) -> None:
    response = client.patch(
        "/api/plants/999/schedule",
        json={"flush_interval_days": 7},
    )
    assert response.status_code == 404


def test_log_older_flush_does_not_change_next_date(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-10"},
    )
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )

    plant_response = client.get(f"/api/plants/{plant['id']}")
    data = plant_response.json()
    assert data["last_flush_date"] == "2026-07-10"
    assert data["next_flush_date"] == "2026-07-17"


def test_delete_latest_flush_recalculates_schedule(client: TestClient, plant: dict) -> None:
    client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    )
    latest_flush = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-10"},
    ).json()
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    client.delete(f"/api/actions/{latest_flush['id']}")

    plant_response = client.get(f"/api/plants/{plant['id']}")
    data = plant_response.json()
    assert data["last_flush_date"] == "2026-07-01"
    assert data["next_flush_date"] == "2026-07-08"


def test_delete_only_flush_clears_next_date(client: TestClient, plant: dict) -> None:
    action = client.post(
        f"/api/plants/{plant['id']}/actions",
        json={"action_type": "flush", "performed_at": "2026-07-01"},
    ).json()
    client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"flush_interval_days": 7},
    )

    client.delete(f"/api/actions/{action['id']}")

    plant_response = client.get(f"/api/plants/{plant['id']}")
    data = plant_response.json()
    assert data["last_flush_date"] is None
    assert data["next_flush_date"] is None
