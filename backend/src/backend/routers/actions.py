from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.db import get_session
from backend.models.action import ActionEntry, ActionType
from backend.models.plant import Plant, utcnow
from backend.services.schedule import refresh_next_flush_date, refresh_next_monitor_date

router = APIRouter(prefix="/api/actions", tags=["actions"])


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(action_id: int, session: Session = Depends(get_session)) -> None:
    action = session.get(ActionEntry, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")

    plant = session.get(Plant, action.plant_id)
    was_flush = action.action_type == ActionType.FLUSH
    was_monitor = action.action_type == ActionType.MONITOR
    session.delete(action)

    if plant is not None and was_flush:
        refresh_next_flush_date(plant, session)
        plant.updated_at = utcnow()
        session.add(plant)
    elif plant is not None and was_monitor:
        refresh_next_monitor_date(plant, session)
        plant.updated_at = utcnow()
        session.add(plant)

    session.commit()
