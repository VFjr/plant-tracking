from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.plant import Plant, PlantCreate, PlantRead, PlantUpdate, utcnow

router = APIRouter(prefix="/api/plants", tags=["plants"])


def _get_plant_or_404(session: Session, plant_id: int) -> Plant:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


@router.get("", response_model=list[PlantRead])
def list_plants(session: Session = Depends(get_session)) -> list[Plant]:
    return list(session.exec(select(Plant).order_by(Plant.name)).all())


@router.post("", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
def create_plant(plant_in: PlantCreate, session: Session = Depends(get_session)) -> Plant:
    plant = Plant.model_validate(plant_in)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant


@router.get("/{plant_id}", response_model=PlantRead)
def get_plant(plant_id: int, session: Session = Depends(get_session)) -> Plant:
    return _get_plant_or_404(session, plant_id)


@router.patch("/{plant_id}", response_model=PlantRead)
def update_plant(
    plant_id: int,
    plant_in: PlantUpdate,
    session: Session = Depends(get_session),
) -> Plant:
    plant = _get_plant_or_404(session, plant_id)
    updates = plant_in.model_dump(exclude_unset=True)
    if not updates:
        return plant
    plant.sqlmodel_update(updates)
    plant.updated_at = utcnow()
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: int, session: Session = Depends(get_session)) -> None:
    plant = _get_plant_or_404(session, plant_id)
    session.delete(plant)
    session.commit()
