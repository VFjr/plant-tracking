from datetime import date

from sqlmodel import Session, select

from backend.models.action import ActionEntry, ActionType
from backend.models.dashboard import DashboardRead, DashboardTask
from backend.models.plant import Plant


def get_flushed_plant_ids(session: Session) -> set[int]:
    rows = session.exec(
        select(ActionEntry.plant_id).where(ActionEntry.action_type == ActionType.FLUSH).distinct()
    ).all()
    return set(rows)


def get_dashboard(session: Session, *, reference_date: date | None = None) -> DashboardRead:
    today = reference_date if reference_date is not None else date.today()

    plants = session.exec(select(Plant).order_by(Plant.name)).all()
    flushed_plant_ids = get_flushed_plant_ids(session)

    overdue: list[DashboardTask] = []
    due_today: list[DashboardTask] = []
    needs_attention: list[DashboardTask] = []

    for plant in plants:
        if plant.id is None:
            continue

        has_flush_interval = plant.flush_interval_days is not None
        has_been_flushed = plant.id in flushed_plant_ids

        if plant.next_flush_date is not None:
            if plant.next_flush_date > today:
                continue

            task = DashboardTask(
                plant_id=plant.id,
                plant_name=plant.name,
                task="flush",
                due_date=plant.next_flush_date,
                has_flush_interval=has_flush_interval,
                has_been_flushed=has_been_flushed,
            )
            if plant.next_flush_date < today:
                overdue.append(task)
            else:
                due_today.append(task)
            continue

        if not has_flush_interval or not has_been_flushed:
            needs_attention.append(
                DashboardTask(
                    plant_id=plant.id,
                    plant_name=plant.name,
                    task="flush",
                    due_date=today,
                    has_flush_interval=has_flush_interval,
                    has_been_flushed=has_been_flushed,
                )
            )

    overdue.sort(key=lambda item: item.due_date)
    due_today.sort(key=lambda item: plant_name_key(item))
    needs_attention.sort(key=lambda item: plant_name_key(item))

    return DashboardRead(
        overdue=overdue,
        due_today=due_today,
        needs_attention=needs_attention,
    )


def plant_name_key(task: DashboardTask) -> str:
    return task.plant_name.casefold()
