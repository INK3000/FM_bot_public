from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..strings import multilanguage as _

CB_BACKUP_CANCEL = "backup_cancel"
CB_BACKUP_CONFIRM = "backup_confirm"


def kb_cancel_only(language_code: str) -> InlineKeyboardMarkup:
    """Keyboard shown while waiting for the .sql file."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✖ {_[language_code].KB_CANCEL}",
                    callback_data=CB_BACKUP_CANCEL,
                )
            ]
        ]
    )


def kb_confirm_or_cancel(language_code: str) -> InlineKeyboardMarkup:
    """Keyboard shown while waiting for restore confirmation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"♻ {_[language_code].KB_CONFIRM_RESTORE}",
                    callback_data=CB_BACKUP_CONFIRM,
                ),
                InlineKeyboardButton(
                    text=f"✖ {_[language_code].KB_CANCEL}",
                    callback_data=CB_BACKUP_CANCEL,
                ),
            ]
        ]
    )
