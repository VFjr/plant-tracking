from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from backend.models.plant import utcnow
from backend.models.relations import plant_foreign_key, utc_datetime_column


class ActionType(str, Enum):
    FLUSH = "flush"
    RESERVOIR_REFILL = "reservoir_refill"
    OTHER = "other"


class ActionEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(sa_column=plant_foreign_key())
    action_type: ActionType
    performed_at: date
    notes: str | None = None
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_datetime_column())


class ActionCreate(SQLModel):
    action_type: ActionType
    performed_at: date
    notes: str | None = None


class ActionRead(SQLModel):
    id: int
    plant_id: int
    action_type: ActionType
    performed_at: date
    notes: str | None
    created_at: datetime
