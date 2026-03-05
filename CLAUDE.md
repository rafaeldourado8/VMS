# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GTVision** is a multi-tenant VMS (Video Management System) that combines:
- Live streaming via MediaMTX (RTSP/RTMP → HLS)
- Continuous 24/7 recording in fMP4 format
- VOD playback via HLS (reusing the live player)
- LPR (License Plate Recognition) in real-time and offline
- Multi-tenant data isolation per user

The primary language is Portuguese (Brazilian) for user-facing strings, comments, and variable names in some modules.

---

## Architecture

### Services (Docker Compose)

| Container | Tech | Port | Role |
|---|---|---|---|
| `haproxy` | HAProxy 2.9 | 80, 443, 8404 | Single entry point — routes all traffic |
| `kong` | Kong 3.5 | (internal) | API Gateway (declarative config at `kong/kong.yml`) |
| `backend` | Django 5.2 | 8000 | REST API, admin, business logic |
| `frontend` | React/Vite | 5173 | SPA |
| `mediamtx` | MediaMTX+ffmpeg | 8554, 8888, 8889, 9997 | RTSP ingestion, HLS output, recording |
| `streaming` | FastAPI | 8001 | Provisions cameras on MediaMTX via its API |
| `onvif` | FastAPI | 8005 | ONVIF discovery & PTZ control |
| `storage` | FastAPI | 8003 | Indexes recordings from disk into DB |
| `vod_hls` | FastAPI | 8006 | Converts recorded MP4 → HLS for playback |
| `clips` | FastAPI | 8004 | Generates video clips on demand |
| `recorder` | Python | — | Manages continuous recording sessions |
| `retention_cleanup` | Python | — | Deletes recordings older than retention limit |
| `postgres_db` | PostgreSQL 15 | 5432 | Primary database |
| `redis_cache` | Redis 7 | 6379 | Cache + Celery broker |
| `auto_provision` | Python | — | Loop that provisions cameras in MediaMTX on startup |

**Traffic flow**: All external requests → HAProxy → Kong (for `/api/*`, `/streaming/*`) → Django/FastAPI services. Static files served directly by Nginx. HLS served by MediaMTX via HAProxy.

### Recording Storage Layout

```
/recordings/{camera_id}/{YYYY-MM-DD}/{HH}.mp4
```

MediaMTX writes fMP4 segments (1h each, 2s parts). Retention is managed by `retention_cleanup` service.

### Backend Django Apps

Located under `backend/apps/`:

- **cameras** — Camera CRUD + MediaMTX provisioning via `CameraService`. Cameras auto-provision on create/delete.
- **deteccoes** — LPR detections (`Deteccao` model for OCR results, `LPRDetection` for richer vehicle metadata). Webhook endpoint for external LPR systems.
- **recordings** — `Recording` model indexes files from disk; `views_recordings_api.py` provides timeline API.
- **iam** — Multi-tenant isolation. `TenantIsolation` table controls per-user access to resources. `TenantAwareMixin`/`TenantAwareManager` on models filter by user automatically. `TenantIsolationMiddleware` attaches `request.tenant_user`.
- **usuarios** — Custom user model (`Usuario`) with `role` field (admin/viewer).
- **analytics** — Aggregated stats and charts.
- **dashboard** — Dashboard widgets and cached summaries.
- **clips** — Clip request management (Django side); actual generation is in `services/clips`.
- **configuracoes** — System-level settings.
- **onvif** — ONVIF device integration (Django models + proxy to onvif FastAPI service).
- **notifications** — System alerts via `SystemAlertMiddleware`.
- **thumbnails** — Snapshot management.

### IAM / Multi-Tenancy Pattern

All resource models use `TenantAwareMixin` and `TenantAwareManager`. To query resources for a user:
```python
Camera.objects.for_user(request.user, 'camera')
```
Admins (`is_staff` or `role='admin'`) bypass isolation and see all resources.

### Frontend Structure

`frontend/src/`:
- `components/` — `ui/` (base), `layout/`, `cameras/`, `dashboard/`
- `pages/` — Route-level components
- `services/` — Axios-based API clients
- `store/` — Zustand stores (auth state with JWT persistence in localStorage)
- `hooks/` — Custom React hooks
- `types/` — TypeScript types

JWT access tokens (15 min) + refresh tokens (1 day) with auto-rotation.

---

## Development Commands

### Full Stack (Docker)

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f mediamtx

# HAProxy stats
open http://localhost:8404/stats
```

### Backend (Django)

Run from `backend/` directory. Without PostgreSQL env vars, falls back to SQLite.

```bash
cd backend

# Install deps
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run dev server
python manage.py runserver

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Load IAM permissions
python manage.py load_permissions
```

### Backend Tests (pytest)

```bash
cd backend

# Run all tests
pytest

# Run a single test file
pytest apps/cameras/test/test_views.py

# Run a single test
pytest apps/cameras/test/test_views.py::TestCameraViews::test_create_camera_api

# Run with coverage
pytest --cov=apps

# Run linter
ruff check .
```

Tests use SQLite (no POSTGRES_DB env var) and in-memory cache (Redis replaced by `LocMemCache` via `conftest.py`). The global `conftest.py` at `backend/apps/conftest.py` provides `admin_user`, `viewer_user`, and `api_client` fixtures.

### Frontend

```bash
cd frontend

# Install
npm install --legacy-peer-deps

# Dev server (proxied via Vite to backend/streaming/HLS)
npm run dev

# Type check + build
npm run build

# Lint
npm run lint
```

Copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_URL`, `VITE_STREAMING_URL`, `VITE_HLS_URL`.

---

## Key Conventions

- **Camera name namespacing**: When provisioned in MediaMTX, camera names are prefixed as `{username}_gtvision_{name}` to avoid collisions between tenants.
- **RTSP vs RTMP**: RTSP cameras are pulled by MediaMTX; RTMP cameras push their stream using a `stream_key` generated at creation time.
- **Service communication**: Django backend calls the Streaming FastAPI service (`:8001`) via `httpx` for MediaMTX provisioning. Settings key: `STREAMING_SERVICE_URL`.
- **VOD playback**: The `vod_hls` service (`:8004`) converts recorded MP4 files to HLS on demand; Django calls it via `VOD_SERVICE_URL`.
- **Celery**: Configured but the worker container is commented out in `docker-compose.yml`. Broker is Redis. Results backend is `django-db`.
- **API docs**: Available at `/api/schema/` (drf-spectacular). Admin at `/admin/`.
