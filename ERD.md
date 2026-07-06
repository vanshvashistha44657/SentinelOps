# Entity-Relationship Diagram (ERD)

This document describes the relational model for the SentinelOps SOC database.

## Schema Overview

The relational database is split into four primary logical areas:
1. **IAM (Identity & Access Management)**: Users, Roles, Permissions, Login History, and Audit Logs.
2. **Ingestion & Detection Engine**: Parsed events, Detection Rules, Rule Versions, and Alerts.
3. **Incident & Case Management**: Incidents, Cases, Analyst Notes, Evidence, Attachments, and Playbooks.
4. **Threat Intelligence**: IOC Records, Threat Feeds, and System Settings.

---

## Core Entities and Fields

### `users`
- `id`: UUID (PK)
- `email`: VARCHAR(255) (Unique, Indexed)
- `hashed_password`: VARCHAR(255)
- `full_name`: VARCHAR(255)
- `role_id`: UUID (FK to `roles`)
- `is_active`: BOOLEAN
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### `roles` and `permissions`
- `roles`: `id`, `name` (e.g. SOC_Analyst_L1), `description`
- `permissions`: `id`, `name` (e.g. `alerts:write`), `description`
- `role_permissions` (Join table): `role_id`, `permission_id`

### `alerts`
- `id`: UUID (PK)
- `title`: VARCHAR(255)
- `severity`: VARCHAR(50) (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- `confidence_score`: INT (1-100)
- `status`: VARCHAR(50) (NEW, INVESTIGATING, TRUE_POSITIVE, FALSE_POSITIVE, CLOSED)
- `mitre_attack_mapping`: JSONB (Tactic & Technique IDs)
- `detection_rule_id`: UUID (FK to `detection_rules`)
- `assigned_user_id`: UUID (FK to `users`)
- `source_ip`: VARCHAR(45)
- `destination_ip`: VARCHAR(45)
- `hostname`: VARCHAR(255)
- `username`: VARCHAR(255)
- `raw_event`: JSONB
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### `incidents`
- `id`: UUID (PK)
- `title`: VARCHAR(255)
- `severity`: VARCHAR(50)
- `status`: VARCHAR(50) (OPEN, UNDER_INVESTIGATION, CONTAINED, RESOLVED, CLOSED)
- `summary`: TEXT
- `assigned_user_id`: UUID (FK to `users`)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### `incident_alerts` (Join table)
- `incident_id`: UUID (FK to `incidents`)
- `alert_id`: UUID (FK to `alerts`)

### `ioc_records`
- `id`: UUID (PK)
- `value`: VARCHAR(512) (Unique, Indexed)
- `type`: VARCHAR(50) (IP, DOMAIN, URL, MD5, SHA256)
- `risk_score`: INT (0-100)
- `mitre_attack_mapping`: JSONB
- `description`: TEXT
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP
