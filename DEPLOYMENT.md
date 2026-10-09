# Deployment Guide

This document covers controlled deployment for SentinelOps. The repository
contains local Compose development infrastructure; it does not prove which
provider currently serves a live website.

## Deployment Architecture

```
Internet / Clients
       │
       ▼ (HTTPS / 443)
┌──────────────┐
│  Nginx Proxy │
└──────┬───────┘
       ├──────────────────────────────┐
       ▼ (Forward API Requests)       ▼ (Serve Static Assets)
┌──────────────┐               ┌──────────────┐
│ FastAPI App  │               │ Next.js SSR  │
│ (Port 8000)  │               │ (Port 3000)  │
└──────┬───────┘               └──────────────┘
       ├──────────────────────────────┐
       ▼                              ▼
┌──────────────┐               ┌──────────────┐
│  PostgreSQL  │               │ Redis Cache  │
│  (Database)  │               │  & Broker    │
└──────────────┘               └──────┬───────┘
                                      ▼
                               ┌──────────────┐
                               │ Celery Worker│
                               │  (Background)│
                               └──────────────┘
```

## Docker Compose development/staging

A local/staging `docker-compose.yml` configures the API, PostgreSQL, and Redis:

- **backend**: Runs Alembic and the FastAPI application.
- **db**: PostgreSQL with a named local volume and healthcheck.
- **redis**: Redis with a healthcheck for worker-ready environments.

It does not include a production frontend proxy or a Celery worker deployment.
Use managed PostgreSQL and provider secret management in production. Run
`alembic upgrade head` as an explicit release step after a verified backup;
do not rely on automatic migrations during application boot.

## Production Security Best Practices

1. **Environment Secrets**: Generate secure keys for JWT signing and database passwords. Never check them into Git.
2. **Database Hardening**: Put PostgreSQL inside a private subnet within the Docker network. Only expose port 80/443 on Nginx to the public.
3. **SSL/TLS**: Enable HTTPS using Let's Encrypt or your custom certificates inside Nginx.
4. **Rate Limiting**: Enable rate limiting at the Nginx and FastAPI (Redis-based) levels to prevent brute force.

## Required deployment variables

Set these through the hosting provider's secret/configuration facility:

```text
SECRET_KEY=<long-random-secret>
DATABASE_URL=<managed-postgresql-url>
REDIS_URL=<managed-redis-url>
CORS_ORIGINS=https://<frontend-host>
TRUSTED_HOSTS=<api-host>,<internal-service-hosts>
NETWORK_CONNECTIVITY_TARGET=<approved-target>
```

The frontend requires the non-secret variable
`NEXT_PUBLIC_API_URL=https://<api-host>/api/v1`.

Before release: back up PostgreSQL, restore the backup in an isolated
environment, apply migrations there, run backend and frontend checks, then
apply the same migration to production. Keep the previous application image
available for code rollback. Database rollback should use a tested forward
repair migration or restore, never an unreviewed destructive downgrade.
