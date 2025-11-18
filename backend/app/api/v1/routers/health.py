from fastapi import APIRouter

from app.services.health import HealthService
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse, summary="Simple health check")
async def health_check() -> HealthResponse:
    status = await HealthService().get_status()
    return HealthResponse(**status)
