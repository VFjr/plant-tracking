from datetime import date

from sqlmodel import Session, select

from backend.models.dashboard import DashboardRead, DashboardTask
from backend.models.plant import Plant


def get_dashboard(session: Session, *, reference_date: date | None = None) -> DashboardRead:
    today = reference_date if reference_date is not None else date.today()

    plants = session.exec(
        select(Plant)
        .where(Plant.next_flush_date.is_not(None))  # type: ignore[union-attr]
        .order_by(Plant.name)
    ).all()

    overdue: list[DashboardTask] = []
    due_today: list[DashboardTask] = []

    for plant in plants:
        if plant.id is None or plant.next_flush_date is None:
            continue

        task = DashboardTask(
            plant_id=plant.id,
            plant_name=plant.name,
            task="flush",
            due_date=plant.next_flush_date,
        )

        if plant.next_flush_date < today:
            overdue.append(task)
        elif plant.next_flush_date == today:
            due_today.append(task)

    overdue.sort(key=lambda item: item.due_date)
    due_today.sort(key=lambda item: plant_name_key(item))

    return DashboardRead(overdue=overdue, due_today=due_today)


def plant_name_key(task: DashboardTask) -> str:
    return task.plant_name.casefold()
