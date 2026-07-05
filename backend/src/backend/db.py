from collections.abc import Generator

from sqlmodel import Session, create_engine

from backend.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def init_db() -> None:
    settings.ensure_dirs()


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
