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
   - Run Alembic migrations.
   - Start the FastAPI application.

### 2. Access

- **API**: `http://localhost:8000/api/v1/docs`

---

## Local Development (Without Docker)

*Refer to project README for local development setup if Docker is not used.*
