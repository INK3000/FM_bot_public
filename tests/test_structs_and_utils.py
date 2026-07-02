from types import SimpleNamespace
from typing import Any, cast

import pytest

from bot.app.misc import utils
from bot.app.structs.user import PerfumePreferences, User


def test_user_from_json_decodes_preferences():
    raw = (
        b'{"id_telegram": 42, "username": "user", "first_name": "First", '
        b'"last_name": "Last", "language_code": "en", '
        b'"preferences_perfume": [{"perfume_id": "557", '
        b'"in_wishlist": true, "in_collection": false}]}'
    )

    user = User.from_json(raw)

    assert user.id_telegram == 42
    assert user.preferences_perfume == [
        PerfumePreferences(
            perfume_id="557",
            in_wishlist=True,
            in_collection=False,
        )
    ]


@pytest.mark.parametrize(
    ("callback_data", "expected"),
    [
        ("add_to_wishlist_557", {"user_id": 42, "perfume_id": "557", "in_wishlist": True}),
        (
            "remove_from_collection_972",
            {"user_id": 42, "perfume_id": "972", "in_collection": False},
        ),
    ],
)
def test_prepare_data_parses_preference_callback(callback_data, expected):
    call = SimpleNamespace(data=callback_data, from_user=SimpleNamespace(id=42))

    assert utils.prepare_data(cast(Any, call)) == expected


class _State:
    def __init__(self, user):
        self._user = user

    async def get_data(self):
        return {"user": self._user}


class _AlgoliaResponse:
    results = [
        {
            "objectID": "557",
            "brand": "Narciso Rodriguez",
            "name": "Essence",
            "url_en": "https://example.invalid/essence",
        }
    ]


class _AlgoliaClient:
    def __init__(self):
        self.object_ids = None

    async def get_objects(self, object_ids):
        self.object_ids = object_ids
        return _AlgoliaResponse()


async def test_get_text_list_fetches_only_selected_preferences():
    user = User(
        id_telegram=42,
        username="user",
        first_name="First",
        last_name="Last",
        language_code="en",
        preferences_perfume=[
            PerfumePreferences("972", in_wishlist=False, in_collection=True),
            PerfumePreferences("557", in_wishlist=True, in_collection=False),
        ],
    )
    algolia_client = _AlgoliaClient()

    text_list = await utils.get_text_list(
        cast(Any, _State(user)),
        cast(Any, algolia_client),
        "in_wishlist",
    )

    assert algolia_client.object_ids == ["557"]
    assert text_list == [
        '<b>557:</b> Narciso Rodriguez - <a href="https://example.invalid/essence">Essence</a>'
    ]
