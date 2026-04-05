from typing import Optional

import httpx

from app.core.config import settings


class BrapiService:
    """
    Responsável exclusivamente pela comunicação com a API externa brapi.dev.
    (Single Responsibility Principle)
    """

    def __init__(self) -> None:
        self.base_url = settings.BRAPI_BASE_URL
        self.token = settings.BRAPI_TOKEN

    def _get_params(self, extra: Optional[dict] = None) -> dict:
        params: dict = {}
        if self.token:
            params["token"] = self.token
        if extra:
            params.update(extra)
        return params

    def get_quote(self, symbol: str) -> Optional[dict]:
        """Retorna a cotação atual de um ativo."""
        url = f"{self.base_url}/quote/{symbol.upper()}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=self._get_params())
                response.raise_for_status()
                results = response.json().get("results", [])
                return results[0] if results else None
        except (httpx.HTTPError, Exception):
            return None

    def get_history(self, symbol: str, range_: str = "1mo", interval: str = "1d") -> list:
        """Retorna o histórico de preços de um ativo via brapi."""
        url = f"{self.base_url}/quote/{symbol.upper()}"
        params = self._get_params({"range": range_, "interval": interval})
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                results = response.json().get("results", [])
                if results:
                    return results[0].get("historicalDataPrice", [])
                return []
        except (httpx.HTTPError, Exception):
            return []


brapi_service = BrapiService()
