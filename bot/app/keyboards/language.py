from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

kb_languages = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="en")],
        [InlineKeyboardButton(text="Lietùvių", callback_data="lt")],
        [InlineKeyboardButton(text="Русский", callback_data="ru")],
    ]
)
