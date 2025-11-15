import os
from typing import Any, Dict, Optional

import httpx


class GeodairClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("GEODAIR_API_KEY", "")
        self.timeout_seconds = timeout_seconds

    async def fetch_air_quality(
        self,
        pollutant_code: str,
        start_datetime_iso: str,
        end_datetime_iso: str,
        station_code: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params: Dict[str, Any] = {
            "pollutant": pollutant_code,
            "start": start_datetime_iso,
            "end": end_datetime_iso,
        }
        if station_code:
            params["station"] = station_code
        if extra_params:
            params.update(extra_params)

        # NOTE: The exact Geod'air API endpoint path and parameters must be adjusted
        # according to your account and documentation. See https://www.geodair.fr/donnees/api
        endpoint = f"{self.base_url}/donnees/api"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            # The API may return JSON or a file. Attempt JSON first.
            try:
                return {"data": response.json()}
            except Exception:
                return {"content": response.text}


