from pathlib import Path

import betterlogging as logging
from aiogram import Bot, F, Router, types
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from ..keyboards.backup import (
    CB_BACKUP_CANCEL,
    CB_BACKUP_CONFIRM,
    kb_cancel_only,
    kb_confirm_or_cancel,
)
from ..middlewares.users import UsersAPIMiddleware
from ..misc.pg_backup import dump_db, restore_db
from ..misc.utils import get_language_code
from ..settings import settings
from ..states.backup import BackupForm
from ..strings import multilanguage as _
from ..structs.user import User

logger = logging.getLogger(__name__)
router = Router()

MAX_RESTORE_FILE_BYTES = 20 * 1024 * 1024


async def _lang(state: FSMContext) -> str:
    data = await state.get_data()
    user: User | None = data.get("user")
    return await get_language_code(user) if user else "en"


def _cleanup_tmp(path_str: str | None) -> None:
    if not path_str:
        return
    try:
        Path(path_str).unlink(missing_ok=True)
    except OSError:
        logger.exception("Failed to remove tmp backup file: %s", path_str)


# ---------- /backup ----------


async def cmd_backup(message: types.Message, state: FSMContext, bot: Bot) -> None:
    lang = await _lang(state)
    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    status = await message.answer(_[lang].BACKUP_IN_PROGRESS)
    dump_path: Path | None = None
    try:
        dump_path = await dump_db()
        await message.answer_document(
            document=types.FSInputFile(
                str(dump_path), filename=dump_path.name,
            ),
        )
    except Exception as exc:  # noqa: BLE001 — surface any subprocess / IO failure to admin
        logger.exception("Backup failed")
        await message.answer(_[lang].BACKUP_FAILED.format(error=str(exc)))
    finally:
        if dump_path is not None:
            _cleanup_tmp(str(dump_path))
        try:
            await status.delete()
        except Exception:  # noqa: BLE001
            pass


# ---------- /restore flow ----------


async def cmd_restore(message: types.Message, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(BackupForm.waiting_for_file)
    await state.update_data(restore_path=None)
    await message.answer(
        _[lang].RESTORE_SEND_FILE,
        reply_markup=kb_cancel_only(lang),
    )


async def on_restore_document(
    message: types.Message, state: FSMContext, bot: Bot
) -> None:
    lang = await _lang(state)
    document = message.document
    if document is None or not (document.file_name or "").lower().endswith(".sql"):
        await message.answer(
            _[lang].RESTORE_INVALID_FILE, reply_markup=kb_cancel_only(lang),
        )
        return
    if (document.file_size or 0) > MAX_RESTORE_FILE_BYTES:
        await message.answer(
            _[lang].RESTORE_FILE_TOO_LARGE, reply_markup=kb_cancel_only(lang),
        )
        return

    tmp_path = Path("/tmp") / f"fm_restore_{document.file_unique_id}.sql"
    await bot.download(document, destination=tmp_path)

    await state.set_state(BackupForm.waiting_for_confirmation)
    await state.update_data(restore_path=str(tmp_path))

    size_kb = max(1, (document.file_size or 0) // 1024)
    await message.answer(
        _[lang].RESTORE_CONFIRM.format(name=document.file_name, size_kb=size_kb),
        reply_markup=kb_confirm_or_cancel(lang),
    )


async def on_restore_waiting_other(message: types.Message, state: FSMContext) -> None:
    """Any non-document message while waiting for the file."""
    lang = await _lang(state)
    await message.answer(
        _[lang].RESTORE_WAITING_HINT, reply_markup=kb_cancel_only(lang),
    )


async def on_confirm_waiting_other(
    message: types.Message, state: FSMContext,
) -> None:
    """Any non-callback message while waiting for confirmation."""
    lang = await _lang(state)
    await message.answer(
        _[lang].RESTORE_CONFIRM_HINT, reply_markup=kb_confirm_or_cancel(lang),
    )


async def on_backup_confirm(
    call: types.CallbackQuery, state: FSMContext, bot: Bot,
) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    path_str: str | None = data.get("restore_path")
    await call.answer()
    assert call.message is not None
    try:
        await call.message.edit_reply_markup(reply_markup=None)  # pyright: ignore[reportAttributeAccessIssue]
    except Exception:  # noqa: BLE001 — stale message, ignore
        pass

    if not path_str or not Path(path_str).exists():
        await call.message.answer(  # pyright: ignore[reportAttributeAccessIssue]
            _[lang].RESTORE_FAILED.format(error="temporary file missing"),
        )
        await state.clear()
        return

    await bot.send_chat_action(call.message.chat.id, ChatAction.TYPING)  # pyright: ignore[reportAttributeAccessIssue]
    status = await call.message.answer(_[lang].RESTORE_IN_PROGRESS)  # pyright: ignore[reportAttributeAccessIssue]
    try:
        await restore_db(Path(path_str))
        UsersAPIMiddleware.cached_users_id.clear()
        await call.message.answer(_[lang].RESTORE_SUCCESS)  # pyright: ignore[reportAttributeAccessIssue]
    except Exception as exc:  # noqa: BLE001
        logger.exception("Restore failed")
        await call.message.answer(  # pyright: ignore[reportAttributeAccessIssue]
            _[lang].RESTORE_FAILED.format(error=str(exc)),
        )
    finally:
        _cleanup_tmp(path_str)
        try:
            await status.delete()
        except Exception:  # noqa: BLE001
            pass
        await state.clear()


async def on_backup_cancel(
    call: types.CallbackQuery, state: FSMContext,
) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    _cleanup_tmp(data.get("restore_path"))
    await call.answer()
    assert call.message is not None
    try:
        await call.message.edit_reply_markup(reply_markup=None)  # pyright: ignore[reportAttributeAccessIssue]
    except Exception:  # noqa: BLE001
        pass
    await call.message.answer(_[lang].RESTORE_CANCELLED)  # pyright: ignore[reportAttributeAccessIssue]
    await state.clear()


# ---------- Router wiring ----------

router.message.register(
    cmd_backup,
    F.from_user.id.in_(settings.bot.admins) & F.text.lower().contains("/backup"),
)
router.message.register(
    cmd_restore,
    F.from_user.id.in_(settings.bot.admins) & F.text.lower().contains("/restore"),
)

router.message.register(
    on_restore_document,
    StateFilter(BackupForm.waiting_for_file),
    F.document,
)
router.message.register(
    on_restore_waiting_other,
    StateFilter(BackupForm.waiting_for_file),
)
router.message.register(
    on_confirm_waiting_other,
    StateFilter(BackupForm.waiting_for_confirmation),
)

router.callback_query.register(
    on_backup_confirm,
    F.data == CB_BACKUP_CONFIRM,
    F.from_user.id.in_(settings.bot.admins),
)
router.callback_query.register(
    on_backup_cancel,
    F.data == CB_BACKUP_CANCEL,
    F.from_user.id.in_(settings.bot.admins),
)
