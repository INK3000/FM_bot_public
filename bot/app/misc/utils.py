from operator import attrgetter
from typing import Any, cast

from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.app.misc.algolia import AlgoliaClient

from ..structs.user import PerfumePreferences, User


def on_startup():
    return None


def on_shutdown():
    return None


def get_chunks(lst: list[str], chunk_size: int) -> list[list[str]]:
    """
    Split list into chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


# language management
async def get_language_code(user: User) -> str:
    """
    Get user language from User object, usually  from FSMContext state.data
    """
    if not user:
        return "en"
    return user.language_code


# perfume_preferences management
async def get_preferences_perfume_list(state: FSMContext) -> list[PerfumePreferences]:
    data = await state.get_data()
    user = data.get("user")
    preferences_perfume = getattr(user, "preferences_perfume", [])
    return preferences_perfume


def get_action(call: types.CallbackQuery) -> bool:
    """
    Get action from callback data
    returns: True if action is add, False if action is remove
    """
    action_name = call.data.split("_")[0]  # pyright: ignore[reportOptionalMemberAccess]
    if action_name.lower() == "add":
        return True
    elif action_name.lower() == "remove":
        return False
    else:
        raise ValueError(f"Unknown action: {action_name}")


def get_target(call: types.CallbackQuery) -> str:
    """
    Get target name from callback data
    returns: "in_wishlist" or "in_collection"
    """
    target_name = call.data.split("_")[-2]  # pyright: ignore[reportOptionalMemberAccess]
    return f"in_{target_name}"


def prepare_data(call: types.CallbackQuery) -> dict[str, int | str | bool]:
    """
    Prepare data for upsert_perfume_preference request
    """
    user_id = call.from_user.id
    perfume_id = str(call.data.split("_")[-1])  # pyright: ignore[reportOptionalMemberAccess]
    action = get_action(call)
    target = get_target(call)
    body = {"user_id": user_id, "perfume_id": perfume_id, target: action}
    return body


# for showing wishlist and collection
async def get_text_list(
    state: FSMContext, algolia_client: AlgoliaClient, attr_name: str
) -> list[str] | None:
    data = await state.get_data()
    user: User | None = data.get("user")

    if not user:
        return
    language_code = await get_language_code(user)

    sorted_list = sorted(user.preferences_perfume, key=lambda p: p.perfume_id)
    filtered_list = filter(attrgetter(attr_name), sorted_list)
    list_ids = [str(p.perfume_id) for p in filtered_list]

    if not list_ids:
        return

    response = await algolia_client.get_objects(list_ids)

    if not response.results:
        return

    # list of strings. for example: 1: brand - name
    text_template = '<b>{object_id}:</b> {brand} - <a href="{url}">{name}</a>'

    results = cast(list[dict[str, Any]], response.results)
    text_list = [
        text_template.format(
            object_id=perfume["objectID"],
            name=perfume["name"],
            brand=perfume["brand"],
            url=perfume[f"url_{language_code}"],
        )
        for perfume in results
    ]
    return text_list
