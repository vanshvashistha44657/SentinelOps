# SentinelOps

SentinelOps is a production-quality, enterprise-grade Security Operations Center (SOC) platform designed to simulate real security operations.

## Core Features

- **Event Pipeline**: Normalization, parsing, enrichment, and real-time detection rule execution.
- **Detection Engine**: Real-time correlation with MITRE ATT&CK mapping, severity-based alerting, and false-positive filtering.
- **Incident & Case Management**: Advanced analyst workflows, notes, timeline tracking, evidence collection, and playbook integration.
- **Threat Intelligence**: Offline-capable IOC analysis and enrichment.
- **Dashboard**: High-fidelity security metrics, analyst workload tracking, and MITRE heatmaps.

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