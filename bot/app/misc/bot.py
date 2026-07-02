from aiogram.types import BotCommand


def get_bot_commands() -> list[BotCommand]:
    commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="language", description="Choose language"),
        BotCommand(command="wishlist", description="Show my wishlist"),
        BotCommand(command="collection", description="Show my collection"),
    ]
    return commands
