from sqlalchemy import Column, DateTime, ForeignKey, Integer


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
