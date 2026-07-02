import asyncio

import asyncpg
import betterlogging as logging
import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.chat_action import ChatActionMiddleware

from .app import handlers
from .app import middlewares as mw
from .app.misc import utils
from .app.misc.algolia import AlgoliaClient
from .app.misc.bot import get_bot_commands
from .app.scheduler.app import main_scheduler
from .app.settings import settings

logger = logging.getLogger(__name__)
if settings.debug:
    logging.basic_colorized_config(level=logging.DEBUG)
else:
    logging.basic_colorized_config(level=logging.INFO)


def configure_sentry() -> None:
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0,
        )


async def main():
    configure_sentry()

    default_bot_properties = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=settings.bot.token, default=default_bot_properties)

    await bot.set_my_commands(
        commands=get_bot_commands(),
    )
    dp = Dispatcher()

    dp.startup.register(utils.on_startup)
    dp.shutdown.register(utils.on_shutdown)

    dp.include_routers(
        handlers.cmd_start.router,
        handlers.cmd_language.router,
        handlers.cmd_show_wishlist.router,
        handlers.cmd_show_collection.router,
        handlers.cmd_clear_cache.router,
        handlers.cmd_backup_restore.router,
        handlers.ech_perfume.router,
        handlers.perf_preferences.router,
    )

    dp.message.middleware(ChatActionMiddleware())
    dp.callback_query.middleware(ChatActionMiddleware())
    dp.message.middleware(mw.UsersAPIMiddleware())
    dp.callback_query.middleware(mw.UsersAPIMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)

    main_scheduler.ctx.add_instance(bot, Bot)
    main_scheduler.start()
    async with asyncpg.create_pool(settings.db.dsn) as pool:
        async with AlgoliaClient(settings) as algolia_client:
            await dp.start_polling(bot, connection=pool, algolia_client=algolia_client)


if __name__ == "__main__":
    asyncio.run(main())
