# Deployment Guide

This document covers production-ready deployment configurations for the SentinelOps platform.

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

## Docker Compose Production

A production-grade `docker-compose.yml` configures all containers securely:

- **api**: Runs the FastAPI app via `gunicorn` with `uvicorn.workers.UvicornWorker`.
- **web**: Runs Next.js or serves frontend build via Nginx.
- **worker**: Celery worker dedicated to log ingestion and parsing.
- **beat**: Celery beat for scheduling threat feed synchronization.
- **db**: Hardened PostgreSQL instance.
- **redis**: Secure Redis container with password authentication.

## Production Security Best Practices

1. **Environment Secrets**: Generate secure keys for JWT signing and database passwords. Never check them into Git.
2. **Database Hardening**: Put PostgreSQL inside a private subnet within the Docker network. Only expose port 80/443 on Nginx to the public.
3. **SSL/TLS**: Enable HTTPS using Let's Encrypt or your custom certificates inside Nginx.
4. **Rate Limiting**: Enable rate limiting at the Nginx and FastAPI (Redis-based) levels to prevent brute force.
