from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.models.action import ActionEntry, ActionType
from backend.models.plant import ManagedKind, Plant, PlantRead, PlantScheduleUpdate


def compute_next_due(last_performed: date, interval_days: int) -> date:
    return last_performed + timedelta(days=interval_days)


def get_last_flush_date(session: Session, plant_id: int) -> date | None:
    action = session.exec(
        select(ActionEntry)
        .where(ActionEntry.plant_id == plant_id, ActionEntry.action_type == ActionType.FLUSH)
        .order_by(ActionEntry.performed_at.desc(), ActionEntry.created_at.desc())
    ).first()
    return action.performed_at if action else None


def get_last_monitor_date(session: Session, plant_id: int) -> date | None:
    action = session.exec(
        select(ActionEntry)
        .where(ActionEntry.plant_id == plant_id, ActionEntry.action_type == ActionType.MONITOR)
        .order_by(ActionEntry.performed_at.desc(), ActionEntry.created_at.desc())
    ).first()
    return action.performed_at if action else None


def refresh_next_flush_date(plant: Plant, session: Session) -> None:
    if plant.flush_interval_days is None:
        plant.next_flush_date = None
        return

    if plant.id is None:
        plant.next_flush_date = None
        return

    last_flush = get_last_flush_date(session, plant.id)
    if last_flush is None:
        plant.next_flush_date = None
        return

    plant.next_flush_date = compute_next_due(last_flush, plant.flush_interval_days)


def refresh_next_monitor_date(plant: Plant, session: Session) -> None:
    if plant.monitor_interval_days is None:
        plant.next_monitor_date = None
        return

    if plant.id is None:
        plant.next_monitor_date = None
        return

    last_monitor = get_last_monitor_date(session, plant.id)
    if last_monitor is None:
        plant.next_monitor_date = None
        return

    plant.next_monitor_date = compute_next_due(last_monitor, plant.monitor_interval_days)


def apply_schedule_update(
    plant: Plant,
    schedule_in: PlantScheduleUpdate,
    session: Session,
) -> None:
    data = schedule_in.model_dump(exclude_unset=True)
    if not data:
        return

    if plant.kind == ManagedKind.SEMI_HYDRO:
        if "monitor_interval_days" in data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="monitor_interval_days is not valid for semi-hydro plants",
            )
        if "flush_interval_days" in data:
            plant.flush_interval_days = data["flush_interval_days"]
        refresh_next_flush_date(plant, session)
        return

    if "flush_interval_days" in data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="flush_interval_days is not valid for cuttings",
        )
    if "monitor_interval_days" in data:
        plant.monitor_interval_days = data["monitor_interval_days"]
    refresh_next_monitor_date(plant, session)


def advance_flush_on_action(plant: Plant, action: ActionEntry, session: Session) -> None:
    if action.action_type != ActionType.FLUSH:
        return
    refresh_next_flush_date(plant, session)


def advance_monitor_on_action(plant: Plant, action: ActionEntry, session: Session) -> None:
    if action.action_type != ActionType.MONITOR:
        return
    refresh_next_monitor_date(plant, session)


def plant_to_read(plant: Plant, session: Session) -> PlantRead:
    last_flush_date = None
    last_monitor_date = None
    if plant.id is not None:
        last_flush_date = get_last_flush_date(session, plant.id)
        last_monitor_date = get_last_monitor_date(session, plant.id)

    return PlantRead(
        id=plant.id,  # type: ignore[arg-type]
        name=plant.name,
        kind=plant.kind,
        species=plant.species,
        location=plant.location,
        description=plant.description,
        flush_interval_days=plant.flush_interval_days,
        next_flush_date=plant.next_flush_date,
        last_flush_date=last_flush_date,
        monitor_interval_days=plant.monitor_interval_days,
        next_monitor_date=plant.next_monitor_date,
        last_monitor_date=last_monitor_date,
        created_at=plant.created_at,
        updated_at=plant.updated_at,
    )
