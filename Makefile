.PHONY: dev-api dev-web migrate test docker-build docker-up docker-down

dev-api:
	cd backend && uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npm run dev

migrate:
	cd backend && uv run alembic upgrade head

test:
	cd backend && uv run pytest

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
