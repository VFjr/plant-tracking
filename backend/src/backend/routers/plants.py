from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.note import Note, NoteCreate, NoteRead
from backend.models.plant import Plant, PlantCreate, PlantRead, PlantScheduleUpdate, PlantUpdate, utcnow
from backend.routers.deps import get_plant_or_404
from backend.services.photos import delete_plant_photo_dir
from backend.services.schedule import apply_schedule_update, plant_to_read

router = APIRouter(prefix="/api/plants", tags=["plants"])


@router.get("", response_model=list[PlantRead])
def list_plants(session: Session = Depends(get_session)) -> list[PlantRead]:
    plants = list(session.exec(select(Plant).order_by(Plant.name)).all())
    return [plant_to_read(plant, session) for plant in plants]


@router.post("", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
def create_plant(plant_in: PlantCreate, session: Session = Depends(get_session)) -> PlantRead:
    plant = Plant.model_validate(plant_in)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant_to_read(plant, session)


@router.get("/{plant_id}", response_model=PlantRead)
def get_plant(plant_id: int, session: Session = Depends(get_session)) -> PlantRead:
    plant = get_plant_or_404(session, plant_id)
    return plant_to_read(plant, session)


@router.patch("/{plant_id}", response_model=PlantRead)
def update_plant(
    plant_id: int,
    plant_in: PlantUpdate,
    session: Session = Depends(get_session),
) -> PlantRead:
    plant = get_plant_or_404(session, plant_id)
    updates = plant_in.model_dump(exclude_unset=True)
    if not updates:
        return plant_to_read(plant, session)
    plant.sqlmodel_update(updates)
    plant.updated_at = utcnow()
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant_to_read(plant, session)


@router.patch("/{plant_id}/schedule", response_model=PlantRead)
def update_plant_schedule(
    plant_id: int,
    schedule_in: PlantScheduleUpdate,
    session: Session = Depends(get_session),
) -> PlantRead:
    plant = get_plant_or_404(session, plant_id)
    if not schedule_in.model_dump(exclude_unset=True):
        return plant_to_read(plant, session)
    apply_schedule_update(plant, schedule_in, session)
    plant.updated_at = utcnow()
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant_to_read(plant, session)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: int, session: Session = Depends(get_session)) -> None:
    plant = get_plant_or_404(session, plant_id)
    delete_plant_photo_dir(plant_id)
    session.delete(plant)
    session.commit()


plants_router = router


@router.get("/{plant_id}/notes", response_model=list[NoteRead])
def list_notes(plant_id: int, session: Session = Depends(get_session)) -> list[Note]:
    get_plant_or_404(session, plant_id)
    return list(
        session.exec(
            select(Note).where(Note.plant_id == plant_id).order_by(Note.created_at.desc())
        ).all()
    )


@router.post("/{plant_id}/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    plant_id: int,
    note_in: NoteCreate,
    session: Session = Depends(get_session),
) -> Note:
    get_plant_or_404(session, plant_id)
    note = Note(plant_id=plant_id, content=note_in.content)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
