from typing import Protocol


class ServiceProtocol(Protocol):
    async def upsert_user(self, data) -> dict: ...

    async def upsert_perfume_preference(self, data): ...
