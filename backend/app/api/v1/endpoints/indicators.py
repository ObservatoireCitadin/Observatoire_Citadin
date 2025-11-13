from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.indicator import Indicator

router = APIRouter()


def serialize_indicator(indicator: Indicator) -> dict:
    return {
        "id": indicator.id,
        "city_id": indicator.city_id,
        "type": indicator.type,
        "value": indicator.value,
        "date": indicator.date.isoformat() if isinstance(indicator.date, date) else None,
        "source": indicator.source,
    }


@router.get("")
def list_indicators(
    city_id: Optional[int] = Query(default=None),
    indicator_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
) -> List[dict]:
    query = db.query(Indicator)

    if city_id is not None:
        query = query.filter(Indicator.city_id == city_id)
    if indicator_type is not None:
        query = query.filter(Indicator.type == indicator_type)

    results = query.order_by(Indicator.date.desc()).limit(1000).all()
    return [serialize_indicator(i) for i in results]


