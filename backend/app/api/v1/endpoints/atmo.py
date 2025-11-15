from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.core.config import get_settings
from app.etl.atmo_client import AtmoClient

router = APIRouter()


@router.get("/indices")
async def get_atmo_indices(
    date: str = Query(..., description="date (YYYY-MM-DD)"),
    date_historique: str = Query(..., description="date_historique (YYYY-MM-DD)"),
    code_zone: Optional[str] = Query(None, description="code_zone"),
) -> Dict[str, Any]:
    # Ensure chronological order: date_historique must be strictly before date
    try:
        d = datetime.fromisoformat(date).date()
        dh = datetime.fromisoformat(date_historique).date()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    if not (dh < d):
        raise HTTPException(status_code=400, detail="'date_historique' must be strictly before 'date'.")
    settings = get_settings()
    client = AtmoClient(
        base_url=settings.ATMO_API_BASE_URL,
        username=settings.ATMO_USERNAME,
        password=settings.ATMO_PASSWORD,
    )

    try:
        raw = await client.fetch_indices_atmo(
            date=d.isoformat(),
            date_historique=dh.isoformat(),
            code_zone=code_zone,
        )
        # Extract only normalized date (from date_maj) and code_qual
        items = []
        if isinstance(raw, dict):
            features = raw.get("features") or []
            for ft in features:
                props = (ft or {}).get("properties") or {}
                date_maj = props.get("date_maj")
                code_qual = props.get("code_qual")
                if date_maj is not None and code_qual is not None:
                    try:
                        dt = datetime.fromisoformat(str(date_maj).replace("Z", "+00:00"))
                        norm_date = dt.date().isoformat()
                    except Exception:
                        norm_date = str(date_maj).split("T")[0] if "T" in str(date_maj) else str(date_maj)
                    items.append({"date": norm_date, "code_qual": code_qual})
        elif isinstance(raw, list):
            for row in raw:
                if not isinstance(row, dict):
                    continue
                date_maj = row.get("date_maj")
                code_qual = row.get("code_qual")
                if date_maj is not None and code_qual is not None:
                    try:
                        dt = datetime.fromisoformat(str(date_maj).replace("Z", "+00:00"))
                        norm_date = dt.date().isoformat()
                    except Exception:
                        norm_date = str(date_maj).split("T")[0] if "T" in str(date_maj) else str(date_maj)
                    items.append({"date": norm_date, "code_qual": code_qual})
        return {"results": items}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ATMO error: {exc}")


