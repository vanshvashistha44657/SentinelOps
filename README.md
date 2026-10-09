# SentinelOps

SentinelOps is a portfolio-focused Security Operations Center (SOC) platform for collecting authorized telemetry, evaluating evidence-based detections, investigating alerts, and documenting response activity.

## Core Features

- **Event Pipeline**: Normalization, parsing, enrichment, and real-time detection rule execution.
- **Detection Engine**: Real-time correlation with MITRE ATT&CK mapping, severity-based alerting, and false-positive filtering.
- **Incident & Case Management**: Advanced analyst workflows, notes, timeline tracking, evidence collection, and playbook integration.
- **Threat Intelligence**: Offline-capable IOC analysis and enrichment.
- **Dashboard**: High-fidelity security metrics, analyst workload tracking, and MITRE heatmaps.
- **Network Intelligence**: Authorized host telemetry, interface snapshots, bounded gateway/DNS checks, neighbor-table discovery, historical observations, and sensor freshness.

## Technology Stack

- **Backend**: Python 3.13+, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Celery, Pydantic v2
- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, Zustand

## Project Structure

```text
sentinelsops/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── core/
│   │   └── utils/
│   ├── tests/
│   └── alembic/
├── frontend/
└── docs/
```

## Capability boundaries

The host sensor reports information exposed by the operating system. ARP and
neighbor tables are limited evidence, not a complete inventory of every device
on a LAN or Wi-Fi network. VLANs, client isolation, sleeping devices, firewall
rules, permissions, and expired neighbor entries can reduce visibility. The
platform does not collect saved Wi-Fi passwords, run intrusive port scans, or
claim that an unfamiliar device is malicious without additional evidence.

## Quick start

1. Copy `backend/.env.example` to `backend/.env` and set a strong local
   `SECRET_KEY` and development `DATABASE_URL`.
2. Start services with `docker compose up --build`.
3. Apply migrations with `docker compose exec backend alembic upgrade head`.
4. Seed roles with `docker compose exec backend python seed_roles.py`.
5. Start the frontend from `frontend/` with `npm install` and `npm run dev`.

The browser API URL is configured with `frontend/.env.example` through
`NEXT_PUBLIC_API_URL`. Do not place secrets in frontend environment variables.

## Host sensor

An administrator enrolls and activates a sensor. Configure the authorized host
with `SENSOR_ID`, `SENSOR_KEY`, and `SENTINELOPS_API_URL`, then run:

```bash
python -m network_sensor
```

The sensor uses bounded OS commands and authenticated API submission. It never
accepts arbitrary commands from the backend.
