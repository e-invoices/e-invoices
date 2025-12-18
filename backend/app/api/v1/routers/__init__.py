from fastapi import APIRouter

from .auth import router as auth_router
from .health import router as health_router
from .organization import router as organization_router
from .user import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(organization_router)
