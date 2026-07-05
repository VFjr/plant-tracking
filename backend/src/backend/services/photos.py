import shutil
import uuid
from io import BytesIO
from pathlib import Path

import pillow_heif
from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError

from backend.config import settings

pillow_heif.register_heif_opener()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_DIMENSION = 1920
JPEG_QUALITY = 85
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}


def plant_photo_dir(plant_id: int) -> Path:
    return Path(settings.upload_dir) / str(plant_id)


def photo_file_path(plant_id: int, stored_name: str) -> Path:
    return plant_photo_dir(plant_id) / stored_name


def optimize_image(data: bytes) -> bytes:
    try:
        with Image.open(BytesIO(data)) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            out = BytesIO()
            img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            return out.getvalue()
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid image file",
        ) from exc


async def read_and_validate_upload(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Empty file",
        )
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )
    return data


def save_optimized_photo(plant_id: int, image_data: bytes) -> str:
    optimized = optimize_image(image_data)
    stored_name = f"{uuid.uuid4().hex}.jpg"
    dest_dir = plant_photo_dir(plant_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / stored_name
    dest_path.write_bytes(optimized)
    return stored_name


def delete_photo_file(plant_id: int, stored_name: str) -> None:
    path = photo_file_path(plant_id, stored_name)
    if path.exists():
        path.unlink()


def delete_plant_photo_dir(plant_id: int) -> None:
    plant_dir = plant_photo_dir(plant_id)
    if plant_dir.exists():
        shutil.rmtree(plant_dir)
