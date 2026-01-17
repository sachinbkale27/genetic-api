"""Health check endpoints."""

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])

API_VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for Kubernetes probes."""
    return HealthResponse(status="healthy", version=API_VERSION)


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness check endpoint for Kubernetes."""
    return HealthResponse(status="ready", version=API_VERSION)
