from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.etl.insee_melodi_client import fetch_melodi_data


router = APIRouter()


# Mapping dictionaries for decoding INSEE codes
SEX_MAPPING = {
    "_T": "Total",
    "F": "Femme",
    "M": "Homme",
}

EMPFORM_MAPPING = {
    "_T": "Total",
    "1": "Non Salariés",
    "2": "Salariés",
}

EMP_ACTIVITY_MAPPING = {
    "_T": "Total",
    "AZ": "Agriculture, sylviculture et pêche",
    "BE": "Industrie manufacturière, industries extractives et autres",
    "FZ": "Construction",
    "GU": "Services principalement marchands",
    "OQ": "Administration publique, enseignement, santé humaine et action sociale",
}

PCS_MAPPING = {
    "_T": "Total",
    "1": "Agriculteurs",
    "2": "Artisans, commerçants et chefs d'entreprise",
    "3": "Cadres et professions intellectuelles supérieures",
    "4": "Professions intermédiaires",
    "5": "Employés",
    "6": "Ouvriers",
}


def decode_emploi_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Décode les valeurs codées dans le DataFrame en leurs libellés complets.
    """
    df = df.copy()
    
    if "SEX" in df.columns:
        df["SEX"] = df["SEX"].map(SEX_MAPPING).fillna(df["SEX"])
    
    if "EMPFORM" in df.columns:
        df["EMPFORM"] = df["EMPFORM"].map(EMPFORM_MAPPING).fillna(df["EMPFORM"])
    
    if "EMP_ACTIVITY" in df.columns:
        df["EMP_ACTIVITY"] = df["EMP_ACTIVITY"].map(EMP_ACTIVITY_MAPPING).fillna(df["EMP_ACTIVITY"])
    
    if "PCS" in df.columns:
        df["PCS"] = df["PCS"].map(PCS_MAPPING).fillna(df["PCS"])
    
    return df


@router.get("/")
async def get_insee_emploi_data(
    geo: Union[str, List[str]] = Query(
        ...,
        description="Paramètre GEO (ex: 'COM-69123' pour Lyon)",
    ),
    time_period: Optional[str] = Query(
        None,
        description="Période temporelle (ex: '2022')",
    ),
    pcs: Optional[str] = Query(
        None,
        description="Profession et catégorie socioprofessionnelle",
    ),
    decode: bool = Query(
        True,
        description="Si True, décode les valeurs codées en libellés",
    ),
) -> Dict[str, Any]:
    """
    Retourne les données d'emploi du dataset DS_RP_EMPLOI_LT_COMP.
    Exemple: /api/v1/insee_emploi/?geo=COM-69123
    """
    try:
        # Build params list for multiple GEO values
        if isinstance(geo, list):
            params = [(k, v) for v in geo for k in ["GEO"]]
        else:
            params = [("GEO", geo)]
        
        # Add optional parameters if provided
        if time_period:
            params.append(("TIME_PERIOD", time_period))
        if pcs:
            params.append(("PCS", pcs))
        
        # Fetch data from INSEE Melodi API as DataFrame
        df = fetch_melodi_data(
            dataset="DS_RP_EMPLOI_LT_COMP",
            params=params,
            as_dataframe=True,
            timeout_seconds=30.0,
        )
        
        # Filter to keep only NBEMP (Nombre d'emplois)
        if "RP_MEASURE" in df.columns:
            df = df[df["RP_MEASURE"] == "NBEMP"]
        
        # Decode values if requested
        if decode:
            df = decode_emploi_data(df)
        
        # Convert DataFrame to dict for JSON response
        return {
            "data": df.to_dict(orient="records"),
            "count": len(df),
        }
    
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors de la récupération des données INSEE: {str(exc)}"
        )
