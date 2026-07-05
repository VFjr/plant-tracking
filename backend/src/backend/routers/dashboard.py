from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.db import get_session
from backend.models.dashboard import DashboardRead
from backend.services.dashboard import get_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardRead)
def read_dashboard(session: Session = Depends(get_session)) -> DashboardRead:
    return get_dashboard(session)
