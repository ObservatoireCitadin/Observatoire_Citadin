from typing import Any, Dict, Optional
import os
from datetime import datetime, timedelta

import httpx


class AtmoClient:
    """
    Client pour l'API Atmo France.
    Documentation: https://admindata.atmo-france.org/api/doc/v2#/
    Endpoint ciblé: data/indices/atmo
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout_seconds: float = 30.0,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("ATMO_API_KEY", "")
        self.timeout_seconds = timeout_seconds
        self.username = username or os.getenv("ATMO_USERNAME", "")
        self.password = password or os.getenv("ATMO_PASSWORD", "")
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        token = self._get_effective_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _get_effective_token(self) -> Optional[str]:
        # Priority: cached token > api_key > None
        if self._token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._token
        if self.api_key:
            return self.api_key
        return None

    async def login(self) -> str:
        """
        Authenticate with /api/login to obtain a 24h token.
        Expects JSON body: { "username": "...", "password": "..." }
        """
        if not self.username or not self.password:
            raise RuntimeError("ATMO credentials missing: set ATMO_USERNAME and ATMO_PASSWORD")

        login_url = f"{self.base_url}/api/login"
        payload = {"username": self.username, "password": self.password}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(login_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("token") or data.get("access_token") or data.get("jwt") or data.get("id_token")
            if not token:
                raise RuntimeError("Unable to parse token from ATMO login response")
            # Cache token for ~24h (slightly less to avoid edge expiry during calls)
            self._token = token
            self._token_expiry = datetime.utcnow() + timedelta(hours=23, minutes=50)
            return token

    async def fetch_indices_atmo(
        self,
        date: str,
        date_historique: str,
        code_zone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Récupère les indices ATMO via l'endpoint data/indices/atmo.
        Paramètres supportés uniquement:
          - date
          - date_historique
          - code_zone
        """
        endpoint = f"{self.base_url}/api/v2/data/indices/atmo"
        params: Dict[str, Any] = {"date": date, "date_historique": date_historique}
        if code_zone:
            params["code_zone"] = code_zone
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            # Ensure we have a token (login if neither cached token nor api_key present)
            if not self._get_effective_token() and self.username and self.password:
                await self.login()
            # First attempt
            response = await client.get(endpoint, params=params, headers=self._headers())
            if response.status_code == 401 and self.username and self.password:
                # Retry once after refreshing token
                await self.login()
                response = await client.get(endpoint, params=params, headers=self._headers())
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                return {"content": response.text}


