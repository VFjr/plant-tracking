from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.action import ActionEntry, ActionType
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
    overdue_plant = Plant(name="Monstera", next_flush_date=date(2026, 6, 28), flush_interval_days=7)
    due_today_plant = Plant(name="Pothos", next_flush_date=date(2026, 7, 5), flush_interval_days=7)
    future_plant = Plant(name="Fern", next_flush_date=date(2026, 7, 12), flush_interval_days=7)
    session.add(overdue_plant)
    session.add(due_today_plant)
    session.add(future_plant)
    session.commit()

    session.add(
        ActionEntry(
            plant_id=overdue_plant.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 6, 21),
        )
    )
    session.add(
        ActionEntry(
            plant_id=due_today_plant.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 6, 28),
        )
    )
    session.add(
        ActionEntry(
            plant_id=future_plant.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 7, 5),
        )
    )
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert len(dashboard.overdue) == 1
    assert dashboard.overdue[0].plant_name == "Monstera"
    assert dashboard.overdue[0].task == "flush"
    assert dashboard.overdue[0].due_date == date(2026, 6, 28)
    assert dashboard.overdue[0].has_flush_interval is True
    assert dashboard.overdue[0].has_been_flushed is True

    assert len(dashboard.due_today) == 1
    assert dashboard.due_today[0].plant_name == "Pothos"
    assert dashboard.due_today[0].due_date == date(2026, 7, 5)
    assert dashboard.due_today[0].has_flush_interval is True
    assert dashboard.due_today[0].has_been_flushed is True
    assert dashboard.needs_attention == []


def test_never_flushed_no_interval_appears_needs_attention(session: Session) -> None:
    session.add(Plant(name="Basil", next_flush_date=None))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert dashboard.overdue == []
    assert dashboard.due_today == []
    assert len(dashboard.needs_attention) == 1
    assert dashboard.needs_attention[0].plant_name == "Basil"
    assert dashboard.needs_attention[0].due_date == date(2026, 7, 5)
    assert dashboard.needs_attention[0].has_flush_interval is False
    assert dashboard.needs_attention[0].has_been_flushed is False


def test_never_flushed_with_interval_appears_needs_attention(session: Session) -> None:
    session.add(Plant(name="Mint", next_flush_date=None, flush_interval_days=7))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert dashboard.due_today == []
    assert len(dashboard.needs_attention) == 1
    assert dashboard.needs_attention[0].plant_name == "Mint"
    assert dashboard.needs_attention[0].due_date == date(2026, 7, 5)
    assert dashboard.needs_attention[0].has_flush_interval is True
    assert dashboard.needs_attention[0].has_been_flushed is False


def test_flushed_without_interval_appears_needs_attention(session: Session) -> None:
    plant = Plant(name="Sage", next_flush_date=None)
    session.add(plant)
    session.commit()
    session.add(
        ActionEntry(
            plant_id=plant.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 7, 1),
        )
    )
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert dashboard.due_today == []
    assert len(dashboard.needs_attention) == 1
    assert dashboard.needs_attention[0].plant_name == "Sage"
    assert dashboard.needs_attention[0].due_date == date(2026, 7, 5)
    assert dashboard.needs_attention[0].has_flush_interval is False
    assert dashboard.needs_attention[0].has_been_flushed is True


def test_attention_tasks_grouped_together(session: Session) -> None:
    basil = Plant(name="Basil", next_flush_date=None)
    mint = Plant(name="Mint", next_flush_date=None, flush_interval_days=7)
    sage = Plant(name="Sage", next_flush_date=None)
    session.add(basil)
    session.add(mint)
    session.add(sage)
    session.commit()
    session.add(
        ActionEntry(
            plant_id=sage.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 7, 1),
        )
    )
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert dashboard.overdue == []
    assert dashboard.due_today == []
    assert [task.plant_name for task in dashboard.needs_attention] == ["Basil", "Mint", "Sage"]


def test_future_scheduled_plant_excluded(session: Session) -> None:
    plant = Plant(name="Fern", next_flush_date=date(2026, 7, 12), flush_interval_days=7)
    session.add(plant)
    session.commit()
    session.add(
        ActionEntry(
            plant_id=plant.id,
            action_type=ActionType.FLUSH,
            performed_at=date(2026, 7, 5),
        )
    )
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert dashboard.overdue == []
    assert dashboard.due_today == []
    assert dashboard.needs_attention == []


def test_overdue_sorted_oldest_first(session: Session) -> None:
    session.add(Plant(name="B", next_flush_date=date(2026, 6, 20), flush_interval_days=7))
    session.add(Plant(name="A", next_flush_date=date(2026, 6, 10), flush_interval_days=7))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert [task.due_date for task in dashboard.overdue] == [
        date(2026, 6, 10),
        date(2026, 6, 20),
    ]


def test_due_today_sorted_by_name(session: Session) -> None:
    session.add(Plant(name="Zebra Plant", next_flush_date=date(2026, 7, 5), flush_interval_days=7))
    session.add(Plant(name="Aloe", next_flush_date=date(2026, 7, 5), flush_interval_days=7))
    session.commit()

    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))

    assert [task.plant_name for task in dashboard.due_today] == ["Aloe", "Zebra Plant"]


def test_empty_dashboard(session: Session) -> None:
    dashboard = get_dashboard(session, reference_date=date(2026, 7, 5))
    assert dashboard.overdue == []
    assert dashboard.due_today == []
    assert dashboard.needs_attention == []


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
    assert data["overdue"][0]["has_flush_interval"] is True
    assert data["overdue"][0]["has_been_flushed"] is True
    assert len(data["due_today"]) == 1
    assert data["due_today"][0]["plant_name"] == "Pothos"
    assert data["due_today"][0]["due_date"] == "2026-07-05"
    assert data["due_today"][0]["has_flush_interval"] is True
    assert data["due_today"][0]["has_been_flushed"] is True
    assert data["needs_attention"] == []
