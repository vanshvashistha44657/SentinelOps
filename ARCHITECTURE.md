# Architecture Design Document

## Clean Architecture Principles

SentinelOps strictly adheres to Clean Architecture principles, decoupling business rules from presentation and infrastructure concerns. Dependencies flow strictly inwards.

```
       ┌──────────────────────────────────────────────┐
       │                 Presentation                 │
       │           (FastAPI Routers, JSON)            │
       └──────────────────────┬───────────────────────┘
                              │
                              ▼
       ┌──────────────────────────────────────────────┐
       │                 Application                  │
       │    (Service Orchestration, DTOs, Interfaces) │
       └──────────────────────┬───────────────────────┘
                              │
                              ▼
       ┌──────────────────────────────────────────────┐
       │                    Domain                    │
       │       (Entities, Value Objects, Rules)       │
       └──────────────────────▲───────────────────────┘
                              │
                              │ (Implements Interfaces)
       ┌──────────────────────┴───────────────────────┐
       │                Infrastructure                │
       │      (PostgreSQL Models, SQLAlchemy, Celery) │
       └──────────────────────────────────────────────┘
```

### 1. Domain Layer (`app/domain`)
- **Enterprise-Wide Business Rules**: Contains the fundamental business entities, enums, value objects, and repository interfaces.
- **Zero Dependencies**: This layer must not import from any outer layer (FastAPI, SQLAlchemy, Pydantic/Schemas, or specific services).

### 2. Application Layer (`app/application`)
- **Use Cases / Application Services**: Coordinates the data flow to and from the domain layer, using domain entities and repository interfaces.
- **Data Transfer Objects (DTOs)**: Inputs and outputs for application use cases.
- **Interfaces**: Definitions of repositories, cache clients, or external service clients.

### 3. Presentation Layer (`app/api`)
- **HTTP / REST Endpoints**: FastAPI routers that handle request payload parsing, authentication, request validation (Pydantic schemas), and calling application services.
- **No Business Logic**: Presentation routers must delegate all business logic to Application Services.

### 4. Infrastructure Layer (`app/infrastructure`)
- **Data Persistence**: SQLAlchemy database models, migrations, and concrete Repository Pattern implementations.
- **External Integration**: Celery tasks, background workers, Redis client, and threat intelligence service integrations.

---

## Technical Decisions & Rationale

- **Repository Pattern**: Abstracting the database access allows us to keep the Domain/Application layers clean of SQLAlchemy details and facilitates easy mocking during unit testing.
- **FastAPI Dependency Injection**: Leveraged for injecting application services, repositories, and authentication contexts directly into route handlers.
- **Alembic**: Hand-crafted migrations to safely manage schema evolution with zero-downtime constraints.
