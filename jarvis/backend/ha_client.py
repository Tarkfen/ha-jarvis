from datetime import datetime, timedelta
import httpx


class HAClient:
    def __init__(self, ha_url: str, ha_token: str):
        self._base = ha_url
        self._client = httpx.AsyncClient(
            base_url=ha_url,
            headers={"Authorization": f"Bearer {ha_token}", "Content-Type": "application/json"},
            timeout=10.0,
        )

    async def close(self):
        await self._client.aclose()

    async def get_states(self) -> list[dict]:
        r = await self._client.get("/api/states")
        r.raise_for_status()
        return r.json()

    async def get_state(self, entity_id: str) -> dict:
        r = await self._client.get(f"/api/states/{entity_id}")
        r.raise_for_status()
        return r.json()

    async def call_service(self, domain: str, service: str, data: dict) -> dict:
        r = await self._client.post(f"/api/services/{domain}/{service}", json=data)
        r.raise_for_status()
        return r.json()

    async def get_history(self, entity_id: str, hours: int = 24) -> list:
        start = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        r = await self._client.get(
            f"/api/history/period/{start}",
            params={"filter_entity_id": entity_id, "minimal_response": "true"},
        )
        r.raise_for_status()
        return r.json()

    async def create_automation(self, automation_id: str, config: dict) -> dict:
        r = await self._client.post(f"/api/config/automation/config/{automation_id}", json=config)
        r.raise_for_status()
        return r.json() if r.text else {}

    async def get_config(self) -> dict:
        r = await self._client.get("/api/config")
        r.raise_for_status()
        return r.json()

    async def ping(self) -> bool:
        try:
            r = await self._client.get("/api/")
            return r.status_code == 200
        except Exception:
            return False
