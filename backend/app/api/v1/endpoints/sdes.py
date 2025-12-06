from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.etl.sdes_client import SdesClient


router = APIRouter()


@router.get("/commune")
async def get_sdes_commune_data(
    code_insee: str = Query(
        ...,
        description="Code INSEE de la ville, ex: 69123",
    ),
    variable_label: str = Query(
        ...,
        description="Libellé de la variable",
    ),
    subfield_label: Optional[str] = Query(
        None,
        description="Libellé du sous-champ (optionnel si non applicable)",
    ),
) -> Dict[str, Any]:
    """
    Retourne la série temporelle pour une commune et une variable.
    - Filtre par code INSEE et libellé de la variable
    - Applique le filtre sous-champ uniquement s'il est fourni (non vide)
    """
    client = SdesClient()
    try:
        df = await client.fetch_commune_dataframe(codgeo_code=code_insee)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur SDES: {exc}")

    expected_cols = {
        "COG_COMMUNE - Code de la zone",
        "Libellé de la variable",
        "Libellé du sous-champ",
    }
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Colonnes manquantes dans la réponse SDES: "
                f"{', '.join(missing)}"
            ),
        )

    mask = (
        (df["COG_COMMUNE - Code de la zone"].astype(str) == str(code_insee))
        & (df["Libellé de la variable"] == variable_label)
    )
    if subfield_label is not None and str(subfield_label).strip() != "":
        mask = mask & (df["Libellé du sous-champ"] == subfield_label)
    filtered = df[mask]
    if filtered.empty:
        return {"results": []}

    year_cols = [
        c
        for c in filtered.columns
        if c.startswith("A") and len(c) == 5 and c[1:].isdigit()
    ]
    if not year_cols:
        return {"results": []}

    series = filtered.iloc[0][year_cols].copy()
    series.index = [c[1:] for c in series.index]
    series = pd.to_numeric(series, errors="coerce")

    items = []
    for year_str, value in sorted(
        series.items(),
        key=lambda kv: int(kv[0]),
    ):
        if pd.isna(value):
            norm_value = None
        else:
            norm_value = (
                int(value)
                if float(value).is_integer()
                else float(value)
            )
        items.append({"year": int(year_str), "value": norm_value})

    return {"results": items}
