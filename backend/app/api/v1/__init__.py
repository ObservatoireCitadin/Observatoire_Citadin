from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.indicators import router as indicators_router


router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(indicators_router, prefix="/indicators", tags=["indicators"])


