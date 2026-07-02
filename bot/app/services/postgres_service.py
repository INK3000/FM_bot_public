from typing import Any

import asyncpg
from msgspec import json

from ..services.service_protocol import ServiceProtocol


class PostgresService(ServiceProtocol):
    def __init__(self, connection_pool: asyncpg.Pool):
        self._pool = connection_pool

    async def upsert_user(self, data: dict[str, Any]) -> bytes:
        """
        Upsert a Telegram user through the database function.
        """
        async with self._pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT api.upsert_user(
                    _id_telegram := $1,
                    _first_name := $2,
                    _last_name := $3,
                    _username := $4,
                    _language_code := $5,
                    _refered_by := $6
                )
                """,
                data.get("_id_telegram"),
                data.get("_first_name"),
                data.get("_last_name"),
                data.get("_username"),
                data.get("_language_code"),
                data.get("_refered_by"),
            )

            # asyncpg may return jsonb as a decoded object; repositories expect bytes.
            if isinstance(result, str):
                return result.encode("utf-8")
            else:
                return json.encode(result)

    async def upsert_perfume_preference(self, data: dict[str, Any]) -> bytes:
        """
        Upsert a user perfume preference through the database function.
        """

        async with self._pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT api.upsert_perfume_preference(
                    _user_id := $1,
                    _perfume_id := $2,
                    _in_wishlist := $3,
                    _in_collection := $4
                )
                """,
                data.get("_user_id"),
                data.get("_perfume_id"),
                data.get("_in_wishlist"),
                data.get("_in_collection"),
            )

            if isinstance(result, str):
                return result.encode("utf-8")
            else:
                return json.encode(result)
