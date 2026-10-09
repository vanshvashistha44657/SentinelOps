# Installation Guide

This document outlines the setup for SentinelOps on Windows.

## Prerequisites

- **Docker Desktop** (with WSL 2 integration)
- **Git**

---

## Deployment Setup

### 1. Run using Docker

The easiest way to run the full stack is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd sentinelsops
   ```

2. Create `.env` from `.env.example` and fill in necessary secrets:
   ```bash
   cp backend/.env.example backend/.env
   ```

3. Launch services:
   ```bash
   docker-compose up -d
   ```
   This will automatically:
   - Build the backend container.
   - Start PostgreSQL and Redis.
    - Start the FastAPI application.

   Apply migrations explicitly after PostgreSQL is healthy:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. Seed roles and permissions once:
   ```bash
   docker-compose exec backend python seed_roles.py
   ```

### 2. Access

- **API**: `http://localhost:8000/api/v1/docs`
- **Frontend**: `http://localhost:3000` after starting Next.js.

---

## Local Development (Without Docker)

For local development without Docker, use a PostgreSQL database represented by
`DATABASE_URL`; SQLite files under `backend/` are legacy test fixtures and are
not the production database.

## Network sensor enrollment

An administrator calls `POST /api/v1/network/sensor/register` with the
`admin:write` permission. The response contains a sensor identifier and a
one-time key. Activate it through the administrator activation endpoint, then
configure the authorized host without committing credentials:

```text
SENTINELOPS_API_URL=https://api.example.invalid
SENSOR_ID=<sensor-id>
SENSOR_KEY=<one-time-key>
DISCOVERY_INTERVAL_SECONDS=30
```

The backend stores a hash of the key. Revoke a compromised sensor and enroll a
new one rather than copying credentials between hosts.
