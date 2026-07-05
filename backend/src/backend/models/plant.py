from datetime import UTC, date, datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from backend.models.relations import utc_datetime_column


def utcnow() -> datetime:
    return datetime.now(UTC)


def _strip_required_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("name must not be empty")
    return stripped


def _strip_optional_name(value: str | None) -> str | None:
    if value is None:
        return None
    return _strip_required_name(value)


class Plant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1)
    species: str | None = None
    location: str | None = None
    description: str | None = None
    flush_interval_days: int | None = Field(default=None, ge=1)
    next_flush_date: date | None = None
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_datetime_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_datetime_column())


class PlantCreate(SQLModel):
    name: str = Field(min_length=1)
    species: str | None = None
    location: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _strip_required_name(value)


class PlantUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1)
    species: str | None = None
    location: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        return _strip_optional_name(value)


class PlantScheduleUpdate(SQLModel):
    flush_interval_days: int | None = Field(default=None, ge=1)


class PlantRead(SQLModel):
    id: int
    name: str
    species: str | None
    location: str | None
    description: str | None
    flush_interval_days: int | None
    next_flush_date: date | None
    last_flush_date: date | None = None
    created_at: datetime
    updated_at: datetime
