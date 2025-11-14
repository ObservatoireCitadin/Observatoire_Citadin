from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.etl.geodair_client import GeodairClient

router = APIRouter()


@router.get("")
async def get_air_quality(
    pollutant_code: str = Query(..., description="Code du polluant (voir Geod'air)"),
    start: str = Query(..., description="Datetime ISO de début, ex: 2025-01-01T00:00:00"),
    end: str = Query(..., description="Datetime ISO de fin, ex: 2025-01-02T00:00:00"),
    station: Optional[str] = Query(None, description="Code station (optionnel)"),
) -> Dict[str, Any]:
    settings = get_settings()
    client = GeodairClient(
        base_url=settings.GEODAIR_API_BASE_URL,
        api_key=settings.GEODAIR_API_KEY or None,
    )
    try:
        result = await client.fetch_air_quality(
            pollutant_code=pollutant_code,
            start_datetime_iso=start,
            end_datetime_iso=end,
            station_code=station,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur Geod'air: {exc}")

    return result


