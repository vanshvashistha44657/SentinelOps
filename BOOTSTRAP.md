# SentinelOps Bootstrap Guide

This guide provides instructions for setting up a brand-new SentinelOps instance from scratch.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Docker & Docker Compose:** For running the backend, database, and other services in containers.
- **Node.js (v18 or later) & npm/pnpm:** For running the frontend development server.
- **Python (3.10 or later):** For running the backend locally (optional, if not using Docker).
- **Git:** For cloning the repository.

## Quick Start with Docker (Recommended)

The easiest way to get SentinelOps up and running is using Docker Compose.

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sentinelsops
   ```

2. **Set up environment variables:**
   Copy the example backend configuration to a real `.env` file:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Note: Review `backend/.env` and update any necessary secrets (e.g., `SECRET_KEY`).*

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```
   This will pull the necessary images and start the database, backend, and any other required services.

4. **Run database migrations:**
   Once the containers are running, apply the Alembic migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Start the frontend:**
   In a new terminal window:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application:**
   Open your browser and navigate to `http://localhost:3000`.

## Manual Local Setup

If you prefer to run services natively:

### 1. Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your `.env` file (see Docker setup).
6. Run migrations: `alembic upgrade head`
7. Start the server: `uvicorn app.main:app --reload`

### 2. Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

## Creating the First Administrator Account

SentinelOps does not come with default credentials for security reasons. You must create the first user via the registration endpoint.

### Method 1: Using the Web UI
1. Navigate to `http://localhost:3000/login`.
2. Look for a registration link (if implemented in your version) or use the API directly.

### Method 2: Using `curl` (Recommended for first admin)
Since the initial user needs administrative privileges, you can register a user and then manually upgrade them via the database or an admin API if available.

**Step 1: Register a new user**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register 
     -H "Content-Type: application/json" 
     -d '{
           "email": "admin@sentinelsops.local",
           "full_name": "System Administrator",
           "password": "ComplexPassword123!"
         }'
```

**Step 2: Elevate to Admin**
Currently, new users are assigned a default role. To make this user an administrator, you will need to update their `role_id` in the database to match the Admin role ID. You can do this via a SQL client (like `psql` or `sqlite3` depending on your setup) or by creating a temporary script.

## Common Troubleshooting

- **Database Connection Errors:** Ensure the database container is running (`docker ps`) and that the credentials in `backend/.env` match the database configuration.
- **Frontend cannot reach Backend:** Check that the `baseURL` in `frontend/lib/api.ts` matches the actual address where your backend is running (usually `http://localhost:8000/api/v1`).
- **CORS Errors:** If you encounter CORS issues, ensure the backend is configured to allow requests from your frontend origin (`http://localhost:3000`).
- **Migration Failures:** If migrations fail, check the Alembic logs or try resetting the database container and starting fresh.
