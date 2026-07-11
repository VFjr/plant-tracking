from datetime import date
from typing import Literal

from sqlmodel import SQLModel


class DashboardTask(SQLModel):
    plant_id: int
    plant_name: str
    task: Literal["flush"]
    due_date: date
    has_flush_interval: bool
    has_been_flushed: bool


class DashboardRead(SQLModel):
    overdue: list[DashboardTask]
    due_today: list[DashboardTask]
    needs_attention: list[DashboardTask]
