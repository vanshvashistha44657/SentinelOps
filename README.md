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

```
sentinelsops/
├── backend/                  # Clean Architecture Backend
│   ├── app/
│   │   ├── api/              # Presentation Layer (Routers, Dependencies)
│   │   ├── application/      # Application Layer (Services, DTOs, Repository Interfaces)
│   │   ├── domain/           # Domain Layer (Entities, Value Objects, Domain Services)
│   │   ├── infrastructure/   # Infrastructure Layer (DB Models, Repositories, Redis, Celery)
│   │   ├── core/             # Core Configuration, Security & Logging
│   │   └── utils/            # Utilities
│   ├── tests/                # Automated Tests
│   └── alembic/              # Database Migrations
├── frontend/                 # Next.js Presentation Client
└── docs/                     # Architectural & API Documentation
```

Refer to `ARCHITECTURE.md` for architectural design decisions.
