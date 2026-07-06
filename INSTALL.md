# Installation Guide

This document outlines the local development setup for SentinelOps backend and frontend components.

## Prerequisites

- **Python**: version 3.13 or higher
- **Node.js**: version 18.x or higher (with npm or pnpm)
- **PostgreSQL**: version 15 or higher
- **Redis**: version 6 or higher (for caching, Celery task queue, and rate limiting)
- **Docker**: Optional, but recommended for running external services (DB, Redis)

---

## Local Development Setup

### 1. Database and Cache (Using Docker Compose)

In the project root, a Docker Compose file can be used to run PostgreSQL and Redis:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

Alternatively, ensure your local PostgreSQL and Redis servers are running and accessible.

### 2. Backend Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure your environment variables. Copy `.env.example` to `.env` and fill in details:
   ```bash
   cp .env.example .env
   ```

5. Run database migrations with Alembic:
   ```bash
   alembic upgrade head
   ```

6. Launch the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### 3. Frontend Installation

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure your environment variables. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

4. Start the Next.js development server:
   ```bash
   npm run dev
   ```
