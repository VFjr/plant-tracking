from datetime import date
from typing import Literal

from sqlmodel import SQLModel


class DashboardTask(SQLModel):
    plant_id: int
    plant_name: str
    task: Literal["flush"]
    due_date: date


class DashboardRead(SQLModel):
    overdue: list[DashboardTask]
    due_today: list[DashboardTask]
