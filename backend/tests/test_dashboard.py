from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.plant import Plant
from backend.services.dashboard import get_dashboard


def _schedule_plant(client: TestClient, plant_id: int, flush_date: str, interval_days: int = 7) -> None:
    client.post(
        f"/api/plants/{plant_id}/actions",
        json={"action_type": "flush", "performed_at": flush_date},
    )
    client.patch(
        f"/api/plants/{plant_id}/schedule",
        json={"flush_interval_days": interval_days},
    )


def test_get_dashboard_overdue_and_due_today(session: Session) -> None:
    overdue_plant = Plant(name="Monstera", next_flush_date=date(2026, 6, 28))
    due_today_plant = Plant(name="Pothos", next_flush_date=date(2026, 7, 5))
    future_plant = Plant(name="Fern", next_flush_date=date(2026, 7, 12))
    unscheduled_plant = Plant(name="Basil", next_flush_date=None)
    session.add(overdue_plant)
    session.add(due_today_plant)
    session.add(future_plant)
    session.add(unscheduled_plant)
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert len(dashboard.overdue) == 1
    assert dashboard.overdue[0].plant_name == "Monstera"
    assert dashboard.overdue[0].task == "flush"
    assert dashboard.overdue[0].due_date == date(2026, 6, 28)

    assert len(dashboard.due_today) == 1
    assert dashboard.due_today[0].plant_name == "Pothos"
    assert dashboard.due_today[0].due_date == date(2026, 7, 5)


def test_overdue_sorted_oldest_first(session: Session) -> None:
    session.add(Plant(name="B", next_flush_date=date(2026, 6, 20)))
    session.add(Plant(name="A", next_flush_date=date(2026, 6, 10)))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert [task.due_date for task in dashboard.overdue] == [
        date(2026, 6, 10),
        date(2026, 6, 20),
    ]


def test_due_today_sorted_by_name(session: Session) -> None:
    session.add(Plant(name="Zebra Plant", next_flush_date=date(2026, 7, 5)))
    session.add(Plant(name="Aloe", next_flush_date=date(2026, 7, 5)))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert [task.plant_name for task in dashboard.due_today] == ["Aloe", "Zebra Plant"]


def test_empty_dashboard(session: Session) -> None:
    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))
    assert dashboard.overdue == []
    assert dashboard.due_today == []


def test_dashboard_api(client: TestClient, plant: dict) -> None:
    other = client.post("/api/plants", json={"name": "Pothos"}).json()
    _schedule_plant(client, plant["id"], "2026-06-20")
    _schedule_plant(client, other["id"], "2026-06-28")

    with patch("backend.services.dashboard.date") as mock_date:
        mock_date.today.return_value = date(2026, 7, 5)
        response = client.get("/api/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert len(data["overdue"]) == 1
    assert data["overdue"][0]["plant_name"] == "Test Plant"
    assert data["overdue"][0]["due_date"] == "2026-06-27"
    assert len(data["due_today"]) == 1
    assert data["due_today"][0]["plant_name"] == "Pothos"
    assert data["due_today"][0]["due_date"] == "2026-07-05"
