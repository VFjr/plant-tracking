.PHONY: dev-api dev-web migrate reset-db test docker-build docker-up docker-down backup

dev-api:
	cd backend && uv run alembic upgrade head && uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npm run dev

migrate:
	cd backend && uv run alembic upgrade head

reset-db:
	cd backend && uv run python -m backend.reset_db

test:
	cd backend && uv run pytest

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

backup:
	./scripts/backup.sh
