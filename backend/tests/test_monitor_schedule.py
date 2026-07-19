from fastapi.testclient import TestClient


def test_set_monitor_schedule_computes_next_from_monitor_action(
    client: TestClient, cutting: dict
) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )

    response = client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monitor_interval_days"] == 3
    assert data["last_monitor_date"] == "2026-07-01"
    assert data["next_monitor_date"] == "2026-07-04"


def test_log_monitor_advances_schedule(client: TestClient, cutting: dict) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    response = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-05"},
    )
    assert response.status_code == 201

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    data = plant_response.json()
    assert data["last_monitor_date"] == "2026-07-05"
    assert data["next_monitor_date"] == "2026-07-08"


def test_log_water_change_does_not_advance_monitor_schedule(
    client: TestClient, cutting: dict
) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "water_change", "performed_at": "2026-07-02"},
    )

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    assert plant_response.json()["next_monitor_date"] == "2026-07-04"


def test_log_monitor_without_interval_does_not_set_next_date(
    client: TestClient, cutting: dict
) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-05"},
    )

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    data = plant_response.json()
    assert data["next_monitor_date"] is None
    assert data["last_monitor_date"] == "2026-07-05"


def test_clear_monitor_interval(client: TestClient, cutting: dict) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    response = client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": None},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monitor_interval_days"] is None
    assert data["next_monitor_date"] is None


def test_monitor_schedule_without_monitor_action_sets_no_next_date(
    client: TestClient, cutting: dict
) -> None:
    response = client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monitor_interval_days"] == 3
    assert data["last_monitor_date"] is None
    assert data["next_monitor_date"] is None


def test_cutting_rejects_flush_interval(client: TestClient, cutting: dict) -> None:
    response = client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"flush_interval_days": 7},
    )
    assert response.status_code == 422


def test_semi_hydro_rejects_monitor_interval(client: TestClient, plant: dict) -> None:
    response = client.patch(
        f"/api/plants/{plant['id']}/schedule",
        json={"monitor_interval_days": 3},
    )
    assert response.status_code == 422


def test_log_older_monitor_does_not_change_next_date(client: TestClient, cutting: dict) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-10"},
    )
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    data = plant_response.json()
    assert data["last_monitor_date"] == "2026-07-10"
    assert data["next_monitor_date"] == "2026-07-13"


def test_delete_latest_monitor_recalculates_schedule(client: TestClient, cutting: dict) -> None:
    client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    )
    latest_monitor = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-10"},
    ).json()
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    client.delete(f"/api/actions/{latest_monitor['id']}")

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    data = plant_response.json()
    assert data["last_monitor_date"] == "2026-07-01"
    assert data["next_monitor_date"] == "2026-07-04"


def test_delete_only_monitor_clears_next_date(client: TestClient, cutting: dict) -> None:
    action = client.post(
        f"/api/plants/{cutting['id']}/actions",
        json={"action_type": "monitor", "performed_at": "2026-07-01"},
    ).json()
    client.patch(
        f"/api/plants/{cutting['id']}/schedule",
        json={"monitor_interval_days": 3},
    )

    client.delete(f"/api/actions/{action['id']}")

    plant_response = client.get(f"/api/plants/{cutting['id']}")
    data = plant_response.json()
    assert data["last_monitor_date"] is None
    assert data["next_monitor_date"] is None
