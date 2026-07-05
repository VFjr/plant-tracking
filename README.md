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
make docker-build
make docker-up
```

Open `http://<server-ip>:8000` from any device on your LAN.

Data persists in `./data/` (SQLite database + photo uploads).

```bash
# Stop
make docker-down

# View logs
docker compose logs -f

# Rebuild after pulling changes
make docker-build && make docker-up
```

The container runs migrations on start and exposes a health check on `/api/health`.

## Proxmox deployment

Goal: run on your home LAN only — no internet exposure, no auth.

### 1. Create an LXC or small VM

On Proxmox, create a container or VM on your LAN. Suggested specs:

- 1 vCPU, 1–2 GB RAM
- 8–16 GB disk
- Ubuntu 24.04 or Debian 12

### 2. Install Docker

Inside the LXC/VM:

```bash
# Ubuntu — see https://docs.docker.com/engine/install/ubuntu/
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# Log out and back in so the docker group applies
```

### 3. Deploy the app

```bash
sudo mkdir -p /opt/plant-tracking
sudo chown $USER:$USER /opt/plant-tracking
cd /opt/plant-tracking

git clone <your-repo-url> .
make docker-build
make docker-up
```

Open `http://<lxc-ip>:8000` from a phone or laptop on the same network.

### 4. LAN-only access

- **Do not** port-forward port 8000 on your router.
- The app is intended for trusted home-network use only.

### 5. Optional: friendly hostname

If you use Pi-hole, AdGuard Home, or router DNS, add a local record:

```
plants.home  →  <lxc-ip>
```

You can put Caddy or nginx in front later for `http://plants.home` — not required for initial setup.

### 6. Updates

```bash
cd /opt/plant-tracking
git pull
make docker-build
make docker-up
```

Your `data/` volume is untouched across rebuilds.

## Backup and restore

Everything important lives in `data/`:

- `data/plant_tracking.db` — SQLite database
- `data/uploads/` — plant photos

### Manual backup

```bash
make backup
```

Writes `backups/plant-tracking-YYYY-MM-DD-HHMMSS.tar.gz` in the repo directory.

Override the destination:

```bash
BACKUP_DIR=/mnt/nas/plant-tracker make backup
```

### Scheduled backup (cron)

On the server, back up to NAS or another Proxmox storage daily:

```cron
0 3 * * * cd /opt/plant-tracking && BACKUP_DIR=/mnt/backups/plant-tracking ./scripts/backup.sh
```

### Restore

```bash
make docker-down
rm -rf data/
tar -xzf backups/plant-tracking-YYYY-MM-DD-HHMMSS.tar.gz
make docker-up
```

## Project layout

```
frontend/     React SPA
backend/      FastAPI app (src/backend/)
data/         Runtime data (gitignored)
scripts/      Backup helper
```

## Phases

- [x] Phase 0 — Scaffolding, health check, Docker
- [x] Phase 1 — Plants CRUD
- [x] Phase 2 — Notes and action log
- [x] Phase 3 — Flush scheduling
- [x] Phase 4 — Photos
- [x] Phase 5 — Dashboard
- [x] Phase 6 — Proxmox deployment notes
- [ ] Phase 7 (later) — Smart reservoir tracking
