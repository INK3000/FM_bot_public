import betterlogging as logging
from aiogram import F, Router, flags, types
from aiogram.fsm.context import FSMContext

from ..misc.utils import get_language_code
from ..settings import settings
from ..strings import multilanguage as _
from ..structs.user import User

logger = logging.getLogger(__name__)

router = Router()


@flags.clear_cache
async def cmd_clear_cache(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    user: User = data["user"]
    language_code = await get_language_code(user)

    await message.answer(
        text=_[language_code].CACHE_CLEARED,
    )


router.message.register(
    cmd_clear_cache,
    F.from_user.id.in_(settings.bot.admins) & F.text.lower().contains("/clear_cache"),
)
