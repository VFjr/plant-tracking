from datetime import date, datetime

from sqlmodel import Field, SQLModel

from backend.models.plant import utcnow
from backend.models.relations import plant_foreign_key, utc_datetime_column


class Photo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(sa_column=plant_foreign_key())
    filename: str
    stored_name: str
    caption: str | None = None
    taken_at: date | None = None
    uploaded_at: datetime = Field(default_factory=utcnow, sa_column=utc_datetime_column())


class PhotoRead(SQLModel):
    id: int
    plant_id: int
    filename: str
    stored_name: str
    caption: str | None
    taken_at: date | None
    uploaded_at: datetime
