from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..strings import multilanguage as _
from ..structs.user import PerfumePreferences


def get_perf_kb(
    perfume_preferences: PerfumePreferences, language_code: str
) -> InlineKeyboardMarkup:
    """
    Return inline keyboard for perfumes preferences

    :param perfume_preferences: PerfumePreferences object
    """
    perfume_id = perfume_preferences.perfume_id

    add_to_wishlist_button = {
        False: InlineKeyboardButton(
            text=f"🩶 {_[language_code].KB_ADD_TO_WISHLIST}",
            callback_data=f"add_to_wishlist_{perfume_id}",
        ),
        True: InlineKeyboardButton(
            text=f"❤️ {_[language_code].KB_REMOVE_FROM_WISHLIST}",
            callback_data=f"remove_from_wishlist_{perfume_id}",
        ),
    }

    add_to_collection_button = {
        False: InlineKeyboardButton(
            text=f"☑️ {_[language_code].KB_ADD_TO_COLLECTION}",
            callback_data=f"add_to_collection_{perfume_id}",
        ),
        True: InlineKeyboardButton(
            text=f"✅ {_[language_code].KB_REMOVE_FROM_COLLECTION}",
            callback_data=f"remove_from_collection_{perfume_id}",
        ),
    }

    keyboard = [
        [
            add_to_wishlist_button[perfume_preferences.in_wishlist],
            add_to_collection_button[perfume_preferences.in_collection],
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
