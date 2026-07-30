import httpx

from config import GATEWAY_URL


class GatewayClient:
    def __init__(self):
        self._client = httpx.AsyncClient(base_url=GATEWAY_URL, timeout=30.0)

    async def ask(self, query: str) -> dict:
        resp = await self._client.post("/api/v1/answer", json={"query": query})
        resp.raise_for_status()
        return resp.json()

    async def get_company(self, inn: str) -> dict | None:
        resp = await self._client.get(f"/api/v1/analytics/company/{inn}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def top_risk(self, limit: int = 10) -> list[dict]:
        resp = await self._client.get(f"/api/v1/analytics/companies/top?limit={limit}")
        resp.raise_for_status()
        return resp.json()

    async def get_signals(self, inn: str) -> dict | None:
        resp = await self._client.get(f"/api/v1/analytics/company/{inn}/signals")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def top_groups(self, limit: int = 5) -> list[dict]:
        resp = await self._client.get(f"/api/v1/analytics/groups/top?limit={limit}")
        resp.raise_for_status()
        return resp.json()

    async def recent_anomalies(self, days: int = 7) -> list[dict]:
        resp = await self._client.get(f"/api/v1/analytics/anomalies/recent?days={days}")
        resp.raise_for_status()
        return resp.json()

    async def compare_companies(self, inn1: str, inn2: str) -> list[dict]:
        resp = await self._client.post(f"/api/v1/analytics/companies/compare?inn1={inn1}&inn2={inn2}")
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
