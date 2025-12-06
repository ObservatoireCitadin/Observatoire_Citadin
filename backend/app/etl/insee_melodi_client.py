

from typing import Any, Dict, List, Optional, Tuple, Union
import requests
import pandas as pd

BASE_URL = "https://api.insee.fr/melodi"


def fetch_melodi_data(
    dataset: str = "DS_RP_POPULATION_PRINC",
    params: Optional[Union[Dict[str, str], List[Tuple[str, str]]]] = None,
    as_dataframe: bool = True,
    timeout_seconds: float = 30.0,
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Appelle l'API publique Melodi (sans jeton) pour un dataset donné.
    Exemple d'URL:
      https://api.insee.fr/melodi/data/DS_RP_POPULATION_PRINC?GEO=COM-69123
      https://api.insee.fr/melodi/data/DS_RP_EMPLOI_LT_COMP?GEO=COM&GEO=2025-AAV2020-002*COM

    Args:
        dataset: Identifiant du dataset Melodi
                 (par défaut: "DS_RP_POPULATION_PRINC").
        params: Paramètres de requête. Peut être un dictionnaire
                (ex: {"GEO": "COM-69123", "TIME_PERIOD": "2022"})
                ou une liste de tuples pour paramètres multiples
                (ex: [("GEO", "COM"), ("GEO", "2025-AAV2020-002*COM")]).
        as_dataframe: Si True, retourne un DataFrame pandas aplati à partir
                      des observations.
        timeout_seconds: Timeout de la requête HTTP en secondes.

    Returns:
        Le JSON de réponse complet (dict) ou un DataFrame pandas si
        as_dataframe=True.
    """
    if params is None:
        params = {}

    url = f"{BASE_URL}/data/{dataset}"
    response = requests.get(url, params=params, timeout=timeout_seconds)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()

    if as_dataframe:
        return observations_to_dataframe(data)
    return data


def observations_to_dataframe(payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Convertit le champ 'observations' du JSON Melodi en DataFrame.
    Aplati les 'dimensions' et extrait les valeurs des 'measures'.
    """
    observations: List[Dict[str, Any]] = payload.get("observations", []) or []
    rows: List[Dict[str, Any]] = []

    for obs in observations:
        dimensions = obs.get("dimensions", {}) or {}
        measures = obs.get("measures", {}) or {}

        flat_row: Dict[str, Any] = {}
        flat_row.update(dimensions)

        # Aplatit toutes les mesures
        # Si la structure est {"value": ...}, on prend la clé "value"
        for measure_name, measure_payload in measures.items():
            value: Any = None
            if isinstance(measure_payload, dict):
                value = measure_payload.get("value", None)
                if value is None:
                    # fallback si la structure diffère
                    value = measure_payload.get("values", None)
            else:
                value = measure_payload
            flat_row[measure_name] = value

        rows.append(flat_row)

    if not rows:
        # Colonnes courantes observées sur DS_RP_POPULATION_PRINC
        return pd.DataFrame(
            columns=[
                "GEO",
                "SEX",
                "TIME_PERIOD",
                "RP_MEASURE",
                "AGE",
                "OBS_VALUE_NIVEAU",
            ]
        )
    return pd.DataFrame(rows)


def fetch_population_principale_by_city(
    city_insee_code: str,
    as_dataframe: bool = False,
    extra_params: Optional[Dict[str, str]] = None,
    timeout_seconds: float = 30.0,
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Raccourci pour interroger le dataset 'DS_RP_POPULATION_PRINC'
    pour une commune.
    """
    params = {"GEO": f"COM-{city_insee_code}"}
    if extra_params:
        params.update(extra_params)
    
    return fetch_melodi_data(
        dataset="DS_RP_POPULATION_PRINC",
        params=params,
        as_dataframe=as_dataframe,
        timeout_seconds=timeout_seconds,
    )
