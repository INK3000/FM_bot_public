import betterlogging as logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from asyncpg import Pool

from ..keyboards.perfume_preferences import get_perf_kb
from ..misc.utils import prepare_data
from ..repos.user import UserRepository
from ..services.postgres_service import PostgresService

logger = logging.getLogger(__name__)

router = Router()


async def manage_perfume_preferences(
    call: types.CallbackQuery,
    state: FSMContext,
    connection: Pool,
) -> None:
    """
    Add or change perfume preferences
    """
    user_repo = UserRepository(PostgresService(connection))

    data = prepare_data(call)
    user = await user_repo.update_perfume_preferences(data)
    language_code = user.language_code
    await state.update_data(user=user)

    text = getattr(call.message, "text", "")
    try:
        perfume_preferences = next(
            filter(
                lambda perfume: perfume.perfume_id == data["perfume_id"],
                user.preferences_perfume,
            )
        )
    except Exception as e:
        logger.error(e)
        call.answer()
        return

    if not isinstance(call.message, types.Message):
        await call.answer()
        return

    await call.answer()
    await call.message.edit_text(
        text=text,
        reply_markup=get_perf_kb(perfume_preferences, language_code),
    )

    # clear user cache after adding perfume to wishlist


router.callback_query.register(
    manage_perfume_preferences,
    F.data.contains("wishlist") | F.data.contains("collection"),
)
