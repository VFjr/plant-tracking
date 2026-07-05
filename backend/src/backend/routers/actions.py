from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.db import get_session
from backend.models.action import ActionEntry

router = APIRouter(prefix="/api/actions", tags=["actions"])


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(action_id: int, session: Session = Depends(get_session)) -> None:
    action = session.get(ActionEntry, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    session.delete(action)
    session.commit()
