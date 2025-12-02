import logging

from app.schemas.health import HealthResponse
from app.services.health import HealthService
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse, summary="Simple health check")
async def health_check() -> HealthResponse:
    status = await HealthService().get_status()
    logger.debug("Health check status: %s", status)
    return HealthResponse(**status)
