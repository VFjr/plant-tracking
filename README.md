# Plant Tracker

Semi-hydroponics plant tracking app for a home LAN server.

## Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, TanStack Query
- **Backend:** FastAPI, SQLModel, SQLite, Alembic
- **Deploy:** Docker Compose

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python)
- [fnm](https://github.com/Schniz/fnm) or Node.js 24+ (local frontend dev)
- Docker + Docker Compose (deployment)

## Local development

```bash
# Terminal 1 — API on http://localhost:8000
make dev-api

# Terminal 2 — frontend on http://localhost:5173
make dev-web

# Run tests
make test

# Apply migrations (when they exist)
make migrate

# Wipe local SQLite DB and recreate schema from migrations
make reset-db
```

Copy `.env.example` to `.env` if you want to override defaults.

`make dev-api` runs Alembic migrations automatically before starting the server. Docker does the same on container start.

## Docker (production on home server)

```bash
cp .env.example .env   # optional
make docker-build
make docker-up
```

Open `http://<server-ip>:8000` from any device on your LAN.

Data persists in `./data/` (SQLite database + photo uploads).

## Project layout

```
frontend/     React SPA
backend/      FastAPI app (src/backend/)
data/         Runtime data (gitignored)
```

## Phases

- [x] Phase 0 — Scaffolding, health check, Docker
- [x] Phase 1 — Plants CRUD
- [x] Phase 2 — Notes and action log
- [ ] Phase 3 — Flush/refill scheduling
- [ ] Phase 4 — Photos
- [ ] Phase 5 — Dashboard
- [ ] Phase 6 — Proxmox deployment notes
