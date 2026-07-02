from datetime import datetime

from aiogram import Bot


async def example_job(bot: Bot, chat_id: int):
    """
    This function will be called every minute and send a current time to the chat with chat_id.

    :param bot: Bot object (will be injected by scheduler)
    :param chat_id: int, must be send as keyword argument
    :return: None

    ==================================================
    How to use it
    In this example we just send a message to the chat with chat_id.

    from app.scheduler.app import main_scheduler
    from app.scheduler.jobs import example_job

    async def cmd_start(message: types.Message, state: FSMContext) -> None:
        kwargs = {"chat_id": message.chat.id}
        main_scheduler.add_job(
            example_job,
            "cron",
            hour="*",
            minute="*",
            second="*/10",
            kwargs=kwargs,
        )
    ==================================================
    """
    await bot.send_message(chat_id=chat_id, text=f"It's {datetime.now()}")
