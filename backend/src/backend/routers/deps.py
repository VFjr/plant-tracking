from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.db import get_session
from backend.models.plant import Plant

router = APIRouter()


def get_plant_or_404(session: Session, plant_id: int) -> Plant:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant
