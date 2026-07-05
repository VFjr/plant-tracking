from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from backend.models.plant import utcnow
from backend.models.relations import plant_foreign_key, utc_datetime_column


def _strip_required_content(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("content must not be empty")
    return stripped


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(sa_column=plant_foreign_key())
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_datetime_column())


class NoteCreate(SQLModel):
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return _strip_required_content(value)


class NoteRead(SQLModel):
    id: int
    plant_id: int
    content: str
    created_at: datetime
