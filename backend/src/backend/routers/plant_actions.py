from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.action import ActionCreate, ActionEntry, ActionRead
from backend.models.note import Note
from backend.routers.deps import get_plant_or_404

router = APIRouter(prefix="/api/plants", tags=["actions"])


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
    get_plant_or_404(session, plant_id)
    action = ActionEntry(plant_id=plant_id, **action_in.model_dump())
    session.add(action)
    session.commit()
    session.refresh(action)
    return action
