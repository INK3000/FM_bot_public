from typing import override

from aiogram import BaseMiddleware, types
from aiogram.dispatcher.flags import get_flag
from betterlogging import logging

from ..repos.user import UserRepository
from ..services.postgres_service import PostgresService

logger = logging.getLogger(__name__)


class UsersAPIMiddleware(BaseMiddleware):
    """
    Middleware for checking and saving users data in DB
    """

    cached_users_id: set[int] = set()

    @override
    async def __call__(self, handler, event: types.Message, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        connection = data["connection"]
        user_repo = UserRepository(PostgresService(connection))

        logger.info("Started UsersAPIMiddleware")
        need_to_clear_cache = get_flag(data, "clear_cache")
        logger.debug(f"{need_to_clear_cache=}")
        if need_to_clear_cache:
            self.cached_users_id.clear()

        state = data["state"]
        user_storage = await state.get_data()
        user = user_storage.get("user")
        assert event.from_user is not None
        id_telegram = event.from_user.id  # pyright: ignore[reportOptionalMemberAccess]

        logger.debug(f"{id_telegram=}")
        logger.debug(f"{user=}")

        if not user or id_telegram not in self.cached_users_id:
            logger.info("Get or create user from API in UsersAPIMiddleware")
            new_user_data = {
                "id_telegram": id_telegram,
                "username": event.from_user.username,
                "first_name": event.from_user.first_name,
                "last_name": event.from_user.last_name,
                "language_code": getattr(event.from_user, "language_code", "en"),
            }

            user = await user_repo.create_or_update(new_user_data)

            await state.update_data(user=user)
            self.cached_users_id.add(id_telegram)

        logger.info("Finished UsersAPIMiddleware")
        return await handler(event, data)
