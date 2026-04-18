import os
import httpx


class ObsidianClient:
    def __init__(self) -> None:
        self.base_url = os.environ.get("OBSIDIAN_API_URL", "https://127.0.0.1:27124")
        api_key = os.environ.get("OBSIDIAN_API_KEY", "")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            verify=False,
        )

    async def create_note(self, path: str, content: str) -> dict:
        response = await self._client.put(
            f"/vault/{path}",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )
        response.raise_for_status()
        return {"path": path, "status": "created"}

    async def search_notes(self, query: str) -> list[dict]:
        response = await self._client.post(
            "/search/simple/",
            params={"query": query},
        )
        response.raise_for_status()
        return response.json()

    async def append_note(self, path: str, content: str) -> dict:
        response = await self._client.post(
            f"/vault/{path}",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )
        response.raise_for_status()
        return {"path": path, "status": "appended"}

    async def patch_note(
        self,
        path: str,
        content: str,
        target_type: str,
        target: str,
        operation: str = "replace",
    ) -> dict:
        response = await self._client.patch(
            f"/vault/{path}",
            content=content,
            headers={
                "Content-Type": "text/markdown",
                "Target-Type": target_type,
                "Target": target,
                "Operation": operation,
            },
        )
        response.raise_for_status()
        return {"path": path, "status": "updated", "operation": operation}

    async def read_note(self, path: str) -> str:
        response = await self._client.get(
            f"/vault/{path}",
            headers={"Accept": "text/markdown"},
        )
        response.raise_for_status()
        return response.text

    async def list_tags(self) -> list[dict]:
        response = await self._client.get("/tags/")
        response.raise_for_status()
        return response.json()

    async def list_commands(self) -> list[dict]:
        response = await self._client.get("/commands/")
        response.raise_for_status()
        return response.json()

    async def execute_command(self, command_id: str) -> dict:
        response = await self._client.post(f"/commands/{command_id}/")
        response.raise_for_status()
        return {"command_id": command_id, "status": "executed"}

    async def open_note(self, path: str) -> dict:
        response = await self._client.post(f"/open/{path}")
        response.raise_for_status()
        return {"path": path, "status": "opened"}

    async def list_notes(self, folder: str = "") -> list:
        path = f"/vault/{folder}" if folder else "/vault/"
        response = await self._client.get(
            path,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    async def get_daily_note(
        self,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> str:
        if year is not None and month is not None and day is not None:
            path = f"/periodic/daily/{year}/{month}/{day}/"
        else:
            path = "/periodic/daily/"
        response = await self._client.get(
            path,
            headers={"Accept": "text/markdown"},
        )
        response.raise_for_status()
        return response.text
