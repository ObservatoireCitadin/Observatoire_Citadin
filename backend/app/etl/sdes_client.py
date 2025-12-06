from typing import Any, Dict, Optional
from io import StringIO

import httpx
import pandas as pd

from app.core.config import get_settings


class SdesClient:
    """
    Client pour l'API Données & Indicateurs du SDES
    (Ministère de la Transition Écologique).
    Documentation:
    https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
        dataset_id: str = "632956d8eae137714f60ae22",
        datafile_rid: str = "318d1042-79c8-4d39-b337-9d261050cf7d",
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.SDES_BASE_URL_API).rstrip("/")
        self.timeout_seconds = timeout_seconds
        # Conservés si besoin d'autres endpoints à l'avenir
        self.dataset_id = dataset_id
        self.datafile_rid = datafile_rid

    async def fetch_commune_dataframe(
        self,
        codgeo_code: str,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Récupère le CSV du fichier datafile et retourne un DataFrame
        pandas filtré
        par code INSEE (CODGEO_CODE).

        Args:
            codgeo_code: Code INSEE de la commune (ex: '69123')
            extra_params: Paramètres additionnels passés à l'API SDES

        Returns:
            pd.DataFrame: Données enrichies (noms/desc/unités de colonnes)
        """
        params: Dict[str, Any] = {
            "withColumnName": "true",
            "withColumnDescription": "true",
            "withColumnUnit": "true",
            "CODGEO_CODE": f"eq:{codgeo_code}",  # opérateur eq:
        }
        if extra_params:
            params.update(extra_params)

        url = f"{self.base_url}/datafiles/{self.datafile_rid}/csv"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            csv_text = resp.text

        df = pd.read_csv(StringIO(csv_text), sep=";")
        return df