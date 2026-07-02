import betterlogging as logging
from aiogram import Router, types
from aiogram import filters as flt
from aiogram.fsm.context import FSMContext

from bot.app.misc.algolia import AlgoliaClient

from ..misc.utils import get_chunks, get_language_code, get_text_list
from ..strings import multilanguage as _

logger = logging.getLogger(__name__)

router = Router()


async def cmd_show_wishlist(
    message: types.Message, algolia_client: AlgoliaClient, state: FSMContext
) -> None:
    data = await state.get_data()
    user = data["user"]
    language_code = await get_language_code(user)
    text_list = await get_text_list(state, algolia_client, "in_wishlist")
    if not text_list:
        await message.answer(_[language_code].WISHLIST_IS_EMPTY)
        return

    await message.answer(_[language_code].THIS_IS_WISHLIST)
    for chunk in get_chunks(text_list, 30):
        await message.answer("\n".join(chunk), disable_web_page_preview=True)


router.message.register(cmd_show_wishlist, flt.Command("wishlist"))
