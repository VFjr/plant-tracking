from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.db import init_db
from backend.routers.actions import router as actions_router
from backend.routers.notes import router as notes_router
from backend.routers.plant_actions import router as plant_actions_router
from backend.routers.plants import router as plants_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Plant Tracking", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plants_router)
app.include_router(plant_actions_router)
app.include_router(notes_router)
app.include_router(actions_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


static_path = Path(settings.static_dir) if settings.static_dir else None
if static_path and static_path.exists():
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
