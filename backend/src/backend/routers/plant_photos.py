from datetime import date

from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.photo import Photo, PhotoRead
from backend.routers.deps import get_plant_or_404
from backend.services.photos import read_and_validate_upload, save_optimized_photo

router = APIRouter(prefix="/api/plants", tags=["photos"])


@router.get("/{plant_id}/photos", response_model=list[PhotoRead])
def list_photos(plant_id: int, session: Session = Depends(get_session)) -> list[Photo]:
    get_plant_or_404(session, plant_id)
    return list(
        session.exec(
            select(Photo)
            .where(Photo.plant_id == plant_id)
            .order_by(Photo.uploaded_at.desc())
        ).all()
    )


@router.post("/{plant_id}/photos", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    plant_id: int,
    file: UploadFile,
    caption: str | None = Form(default=None),
    taken_at: date | None = Form(default=None),
    session: Session = Depends(get_session),
) -> Photo:
    get_plant_or_404(session, plant_id)
    image_data = await read_and_validate_upload(file)
    original_filename = file.filename or "photo.jpg"
    stored_name = save_optimized_photo(plant_id, original_filename, image_data)

    trimmed_caption = caption.strip() if caption else None
    if trimmed_caption == "":
        trimmed_caption = None

    photo = Photo(
        plant_id=plant_id,
        filename=original_filename,
        stored_name=stored_name,
        caption=trimmed_caption,
        taken_at=taken_at,
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo
