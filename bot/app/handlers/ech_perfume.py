import betterlogging as logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from algoliasearch.http.exceptions import RequestException
from algoliasearch.search.models.search_response import SearchResponse

from .. import strings
from ..keyboards.perfume_preferences import get_perf_kb
from ..misc.algolia import AlgoliaClient
from ..misc.utils import get_chunks, get_language_code
from ..structs.user import PerfumePreferences, User

logger = logging.getLogger(__name__)

router = Router()

def get_or_create_perfume_preferences(user: User, perfume_id: str) -> PerfumePreferences:
    try:
        perfume_preferences = next(
            filter(
                lambda i: i.perfume_id == perfume_id,
                user.preferences_perfume,
            )
        )
    except StopIteration:
        perfume_preferences = PerfumePreferences(
            perfume_id=perfume_id,
            in_wishlist=False,
            in_collection=False,
        )
    return perfume_preferences

async def ech_perfume(
    message: types.Message, algolia_client: AlgoliaClient, state: FSMContext
) -> None:
    # TODO: refactor it
    text = getattr(message, "text", "")
    data = await state.get_data()
    user: User = data["user"]
    language_code = await get_language_code(user)

    if len(text) > 50:
        await message.answer(strings.multilanguage[language_code].TOO_LONG_QUERY)
        return

    try:
        result = await algolia_client.get_object(text)
        perfume_preferences = get_or_create_perfume_preferences(user, perfume_id=text)
        description = result[f"description_{language_code}"]
        url = result[f"url_{language_code}"]

        answer_text = strings.multilanguage[language_code].QUERY_FOUND.format(
            number=text,
            brand=result["brand"],
            name=result["name"],
            description=description,
            url=url,
        )
        await message.answer(
            answer_text,
            reply_markup=get_perf_kb(perfume_preferences, language_code),
        )
        return
    except RequestException:
        search_response: SearchResponse = await algolia_client.search(query=text)
        if search_response.nb_hits:
            results = search_response.hits
            text_list = []
            for res in results:
                object_id = res.object_id
                brand = getattr(res, "brand", "")
                name = getattr(res, "name", "")
                url = getattr(res, f"url_{language_code}", "")
                text_list.append(
                    f'<b>{object_id}:</b> {brand} - <a href="{url}">{name}</a>'
                )

            for chunk in get_chunks(text_list, 30):
                await message.answer(
                    "\n".join(chunk), disable_web_page_preview=True
                )
        else:
            await message.answer(strings.multilanguage[language_code].QUERY_NOT_FOUND)


router.message.register(ech_perfume, F.text)
