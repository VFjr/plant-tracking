from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.action import (
    CUTTING_ACTION_TYPES,
    SEMI_HYDRO_ACTION_TYPES,
    ActionCreate,
    ActionEntry,
    ActionRead,
    ActionType,
)
from backend.models.plant import ManagedKind, utcnow
from backend.routers.deps import get_plant_or_404
from backend.services.schedule import advance_flush_on_action, advance_monitor_on_action

router = APIRouter(prefix="/api/plants", tags=["actions"])


def _validate_action_for_kind(kind: ManagedKind, action_type: ActionType) -> None:
    allowed = CUTTING_ACTION_TYPES if kind == ManagedKind.CUTTING else SEMI_HYDRO_ACTION_TYPES
    if action_type not in allowed:
        detail = (
            f"Action type '{action_type.value}' is not valid for cuttings"
            if kind == ManagedKind.CUTTING
            else f"Action type '{action_type.value}' is not valid for semi-hydro plants"
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


@router.get("/{plant_id}/actions", response_model=list[ActionRead])
def list_actions(plant_id: int, session: Session = Depends(get_session)) -> list[ActionEntry]:
    get_plant_or_404(session, plant_id)
    return list(
        session.exec(
            select(ActionEntry)
            .where(ActionEntry.plant_id == plant_id)
            .order_by(ActionEntry.performed_at.desc(), ActionEntry.created_at.desc())
        ).all()
    )


@router.post("/{plant_id}/actions", response_model=ActionRead, status_code=status.HTTP_201_CREATED)
def create_action(
    plant_id: int,
    action_in: ActionCreate,
    session: Session = Depends(get_session),
) -> ActionEntry:
    plant = get_plant_or_404(session, plant_id)
    _validate_action_for_kind(plant.kind, action_in.action_type)

    action = ActionEntry(plant_id=plant_id, **action_in.model_dump())
    session.add(action)

    schedule_updated = False
    if action_in.action_type == ActionType.FLUSH:
        advance_flush_on_action(plant, action, session)
        schedule_updated = True
    elif action_in.action_type == ActionType.MONITOR:
        advance_monitor_on_action(plant, action, session)
        schedule_updated = True

    if schedule_updated:
        plant.updated_at = utcnow()
        session.add(plant)

    session.commit()
    session.refresh(action)
    return action
