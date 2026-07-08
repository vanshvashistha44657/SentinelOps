from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.routers.auth import router as auth_router
from app.api.routers.detection import router as detection_router
from app.api.routers.alerts import router as alerts_router
from app.api.routers.ingestion import router as ingestion_router
from app.api.routers.incidents import router as incidents_router
from app.api.routers.cases import router as cases_router
from app.api.routers.iocs import router as iocs_router
from app.api.routers.threat_intel import router as threat_intel_router
from app.api.routers.hunting import router as hunting_router
from app.api.websocket.router import router as ws_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# State
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"] # Update for production
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(detection_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(cases_router, prefix=settings.API_V1_STR)
app.include_router(iocs_router, prefix=settings.API_V1_STR)
app.include_router(threat_intel_router, prefix=settings.API_V1_STR)
app.include_router(hunting_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}
