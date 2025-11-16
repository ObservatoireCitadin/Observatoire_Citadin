from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.air_quality import router as air_quality_router
from app.api.v1.endpoints.atmo import router as atmo_router
from app.api.v1.endpoints.sdes import router as sdes_router


router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(
    air_quality_router,
    prefix="/air-quality",
    tags=["air_quality"],
)
router.include_router(atmo_router, prefix="/atmo", tags=["atmo"])
router.include_router(sdes_router, prefix="/sdes", tags=["sdes"])