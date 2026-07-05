"""Reset the local SQLite database using the same path as the running app."""

from pathlib import Path

from alembic import command
from alembic.config import Config

from backend.config import PROJECT_ROOT, settings

# Legacy path from when .env.example was loaded as config while cwd was backend/
LEGACY_DB_PATHS = [
    PROJECT_ROOT / "backend" / "data" / "plant_tracking.db",
]


def _unlink_sqlite(path: Path) -> None:
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(f"{path}{suffix}")
        candidate.unlink(missing_ok=True)


def main() -> None:
    db_path = Path(settings.database_url.removeprefix("sqlite:///"))
    paths_to_remove = [db_path, *LEGACY_DB_PATHS]

    for path in paths_to_remove:
        _unlink_sqlite(path)

    settings.ensure_dirs()
    command.upgrade(Config(str(PROJECT_ROOT / "backend" / "alembic.ini")), "head")
    print(f"Database reset at {db_path}")


if __name__ == "__main__":
    main()
