from datetime import date

from sqlmodel import Session, select

from backend.models.action import ActionEntry, ActionType
from backend.models.dashboard import DashboardRead, DashboardTask
from backend.models.plant import ManagedKind, Plant


def get_flushed_plant_ids(session: Session) -> set[int]:
    rows = session.exec(
        select(ActionEntry.plant_id).where(ActionEntry.action_type == ActionType.FLUSH).distinct()
    ).all()
    return set(rows)


def get_monitored_plant_ids(session: Session) -> set[int]:
    rows = session.exec(
        select(ActionEntry.plant_id).where(ActionEntry.action_type == ActionType.MONITOR).distinct()
    ).all()
    return set(rows)


def _append_scheduled_task(
    *,
    plant: Plant,
    task: str,
    due_date: date,
    today: date,
    overdue: list[DashboardTask],
    due_today: list[DashboardTask],
    has_flush_interval: bool | None = None,
    has_been_flushed: bool | None = None,
    has_monitor_interval: bool | None = None,
    has_been_monitored: bool | None = None,
) -> None:
    if plant.id is None:
        return

    dashboard_task = DashboardTask(
        plant_id=plant.id,
        plant_name=plant.name,
        task=task,  # type: ignore[arg-type]
        due_date=due_date,
        has_flush_interval=has_flush_interval,
        has_been_flushed=has_been_flushed,
        has_monitor_interval=has_monitor_interval,
        has_been_monitored=has_been_monitored,
    )
    if due_date < today:
        overdue.append(dashboard_task)
    else:
        due_today.append(dashboard_task)


def get_dashboard(session: Session, *, reference_date: date | None = None) -> DashboardRead:
    today = reference_date if reference_date is not None else date.today()

    plants = session.exec(select(Plant).order_by(Plant.name)).all()
    flushed_plant_ids = get_flushed_plant_ids(session)
    monitored_plant_ids = get_monitored_plant_ids(session)

    overdue: list[DashboardTask] = []
    due_today: list[DashboardTask] = []
    needs_attention: list[DashboardTask] = []

    for plant in plants:
        if plant.id is None:
            continue

        if plant.kind == ManagedKind.CUTTING:
            has_monitor_interval = plant.monitor_interval_days is not None
            has_been_monitored = plant.id in monitored_plant_ids

            if plant.next_monitor_date is not None:
                if plant.next_monitor_date > today:
                    continue

                _append_scheduled_task(
                    plant=plant,
                    task="monitor",
                    due_date=plant.next_monitor_date,
                    today=today,
                    overdue=overdue,
                    due_today=due_today,
                    has_monitor_interval=has_monitor_interval,
                    has_been_monitored=has_been_monitored,
                )
                continue

            if not has_monitor_interval or not has_been_monitored:
                needs_attention.append(
                    DashboardTask(
                        plant_id=plant.id,
                        plant_name=plant.name,
                        task="monitor",
                        due_date=today,
                        has_monitor_interval=has_monitor_interval,
                        has_been_monitored=has_been_monitored,
                    )
                )
            continue

        has_flush_interval = plant.flush_interval_days is not None
        has_been_flushed = plant.id in flushed_plant_ids

        if plant.next_flush_date is not None:
            if plant.next_flush_date > today:
                continue

            _append_scheduled_task(
                plant=plant,
                task="flush",
                due_date=plant.next_flush_date,
                today=today,
                overdue=overdue,
                due_today=due_today,
                has_flush_interval=has_flush_interval,
                has_been_flushed=has_been_flushed,
            )
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
