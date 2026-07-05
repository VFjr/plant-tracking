from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from backend.db import get_session
from backend.models.photo import Photo
from backend.services.photos import delete_photo_file, photo_file_path

router = APIRouter(prefix="/api/photos", tags=["photos"])


@router.get("/{photo_id}/file")
def get_photo_file(photo_id: int, session: Session = Depends(get_session)) -> FileResponse:
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    path = photo_file_path(photo.plant_id, photo.stored_name)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(path, media_type="image/jpeg", filename=photo.filename)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(photo_id: int, session: Session = Depends(get_session)) -> None:
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    delete_photo_file(photo.plant_id, photo.stored_name)
    session.delete(photo)
    session.commit()
