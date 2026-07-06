# Changelog

All notable changes to the SentinelOps project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-07

### Added
- **Phase 1: Architecture and Documentation**:
  - Defined the Clean Architecture structure for the backend (`backend/app`).
  - Authored core architectural specifications: `README.md`, `ARCHITECTURE.md`, `INSTALL.md`, `DEPLOYMENT.md`, `ERD.md`, `API.md`, `CHANGELOG.md`, and `SECURITY.md`.
  - Created initial directory structures for Domain, Application, Presentation, and Infrastructure layers.
- **Phase 2: Database Modeling**:
  - Implemented 22 SQLAlchemy 2.0 declarative models across 5 modules (`iam.py`, `alerts.py`, `incidents.py`, `threat_intel.py`, `system.py`).
  - Added unit tests for model instantiation in `tests/test_models.py`.
- **Phase 3: Backend Foundation**:
  - Created Pydantic schemas for request/response validation (Infrastructure Layer).
  - Defined abstract Repository Interfaces (Domain Layer).
  - Implemented concrete SQLAlchemy Repository for `User` (Infrastructure Layer).
  - Manually configured Alembic for database migration management.
- **Phase 4: Backend Services**:
  - Implemented `AuthService` in Application Layer to orchestrate authentication, user registration, and token generation.
- **Phase 5: Presentation Layer**:
  - Implemented Authentication routers in `backend/app/api/routers/auth.py`.
  - Configured FastAPI dependency injection for `AuthService` and `UserRepository`.
  - Integrated routers into the main FastAPI application entrypoint.
- **Phase 6: Detection Engine Module**:
  - Defined Pydantic schemas for detection rules.
  - Implemented `DetectionRuleRepository` (abstract) and `SQLAlchemyDetectionRuleRepository` (concrete).
  - Created `RuleLoader` utility for YAML-based rule management.
  - Implemented `DetectionService` and `AlertService` for business logic and alert ingestion.
  - Exposed rule management and alert ingestion via FastAPI routers in `api/routers/detection.py` and `api/routers/alerts.py`.
  - Added unit tests for model and repository functionality in `tests/test_detection_engine.py`.
- **Phase 1 (Audit Continuation): Authorization & API Security**:
  - Initiated implementation of fine-grained RBAC and permission-based authorization.
