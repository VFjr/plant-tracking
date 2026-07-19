from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer


def plant_foreign_key(*, index: bool = True) -> Column:
    """FK to plant.id with ON DELETE CASCADE — use for all child tables."""
    return Column(
        Integer,
        ForeignKey("plant.id", ondelete="CASCADE"),
        nullable=False,
        index=index,
    )


def utc_datetime_column() -> Column:
    return Column(DateTime(timezone=True), nullable=False)


def enum_column(
    enum_cls: type[PyEnum],
    *,
    nullable: bool = False,
    server_default: str | None = None,
) -> Column:
    """String-backed enum column that persists Enum.value (matches Alembic String cols)."""
    kwargs: dict[str, Any] = {"nullable": nullable}
    if server_default is not None:
        kwargs["server_default"] = server_default
    return Column(
        SAEnum(
            enum_cls,
            values_callable=lambda members: [member.value for member in members],
            native_enum=False,
        ),
        **kwargs,
    )
