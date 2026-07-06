# API Reference Guide

The SentinelOps backend exposes a REST API built with FastAPI. All requests and responses must communicate in standard JSON.

## Base Paths

- Production API: `https://api.sentinelsops.internal/api/v1`
- Local Development: `http://localhost:8000/api/v1`
- Swagger Documentation: `/docs` (or `/api/v1/docs`)

---

## Endpoint Specifications

### 1. Authentication & IAM (`/auth`)

- `POST /auth/register`: Register a new user (admin/manager restricted).
- `POST /auth/login`: Authenticate and receive JWT access/refresh token pair.
- `POST /auth/refresh`: Refresh expired access token.
- `POST /auth/logout`: Revoke active refresh token.
- `GET /auth/me`: Fetch profile of the currently logged-in user.

### 2. Detection Engine & Alerts (`/alerts`)

- `GET /alerts`: Query, filter, and paginate alerts (filter by severity, status, source/destination IP, analyst).
- `GET /alerts/{id}`: Detailed view of a single alert.
- `PATCH /alerts/{id}`: Update alert state (assign to analyst, update status to TRUE_POSITIVE/FALSE_POSITIVE).
- `POST /alerts/ingest`: Raw log ingestion pipeline endpoint.

### 3. Incident & Case Management (`/incidents`)

- `GET /incidents`: Query all incident cases.
- `POST /incidents`: Group alerts into a formal security incident.
- `GET /incidents/{id}`: Retrieve incident detail, including timeline, analysts, and notes.
- `POST /incidents/{id}/notes`: Add timeline notes/comments.
- `POST /incidents/{id}/evidence`: Attach evidence metadata/hashes or physical file objects.

### 4. Threat Intelligence & IOCs (`/ti`)

- `GET /ti/iocs`: List and search indicators of compromise.
- `POST /ti/iocs`: Manually create/add IOC records.
- `POST /ti/feeds/sync`: Trigger manual update/sync of Threat Intelligence feeds.
