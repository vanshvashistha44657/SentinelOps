from fastapi import FastAPI
from app.core.config import settings
from app.api.routers.auth import router as auth_router
from app.api.routers.detection import router as detection_router
from app.api.routers.alerts import router as alerts_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(detection_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}
