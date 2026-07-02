import betterlogging as logging
from aiogram import Router, types
from aiogram import filters as flt
from aiogram.fsm.context import FSMContext
from asyncpg import Pool

from .. import strings
from ..keyboards.language import kb_languages
from ..repos.user import UserRepository
from ..services.postgres_service import PostgresService
from ..states.language import LanguageForm

logger = logging.getLogger(__name__)

router = Router()


async def cmd_language(message: types.Message, state: FSMContext) -> None:
    await message.answer(text=strings.CHOOSE_LANGUAGE, reply_markup=kb_languages)
    await state.set_state(LanguageForm.language)


async def choose_language(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    connection: Pool,
) -> None:
    user_repo = UserRepository(PostgresService(connection))
    language = callback_query.data
    assert language is not None

    data = await state.get_data()
    user = data.get("user")
    assert user is not None

    user.language_code = language

    await callback_query.answer()

    assert callback_query.message is not None
    await callback_query.message.delete()  # pyright: ignore[reportAttributeAccessIssue]

    data_to_update = {"id_telegram": user.id_telegram, "language_code": language}

    await user_repo.create_or_update(data_to_update)

    await state.set_state(None)

    await callback_query.message.answer(
        text=strings.multilanguage[language].START_GREETINGS,
        reply_markup=types.ReplyKeyboardRemove(),  # type: ignore
    )


router.message.register(cmd_language, flt.Command("language"))
router.message.register(cmd_language, LanguageForm.language)
router.callback_query.register(choose_language, LanguageForm.language)
