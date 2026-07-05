FROM node:24-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
COPY backend/src ./src
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

RUN uv sync --frozen --no-dev

COPY --from=frontend-build /app/frontend/dist ./static

ENV STATIC_DIR=/app/static \
    DATABASE_URL=sqlite:////data/plant_tracking.db \
    UPLOAD_DIR=/data/uploads \
    DATA_DIR=/data

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
