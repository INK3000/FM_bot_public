from typing import cast

from algoliasearch.search.client import SearchClient
from algoliasearch.search.models.get_objects_response import GetObjectsResponse
from algoliasearch.search.models.search_response import SearchResponse

from ..settings import Settings


class AlgoliaClient:
    def __init__(self, app_settings: Settings) -> None:
        self._client: SearchClient = SearchClient(
            app_settings.algolia_search.algolia_app_id,
            app_settings.algolia_search.algolia_backend_api_key,
        )
        self._index: str = app_settings.algolia_search.algolia_index_name

    async def search(self, query: str) -> SearchResponse:
        # https://www.algolia.com/doc/libraries/python/v4/methods/search/search-single-index/?client=python
        return await self._client.search_single_index(
            index_name=self._index, search_params={"query": query}
        )

    async def get_object(self, object_id: str) -> dict[str, str]:
        """Return one perfume object from the configured Algolia index."""
        result = await self._client.get_object(
            index_name=self._index, object_id=object_id
        )
        return cast(dict[str, str], result)

    async def get_objects(self, object_ids: list[str]) -> GetObjectsResponse:
        # https://www.algolia.com/doc/libraries/python/v4/methods/search/get-objects/?client=python
        # response = client.get_objects(
        #     get_objects_params={
        #         "requests": [
        #             {
        #                 "attributesToRetrieve": [
        #                     "attr1",
        #                     "attr2",
        #                 ],
        #                 "objectID": "uniqueID",
        #                 "indexName": "ALGOLIA_INDEX_NAME",
        #             },
        #         ],
        #     },
        # )
        requests = [
            {"objectID": object_id, "indexName": self._index}
            for object_id in object_ids
        ]
        return await self._client.get_objects(get_objects_params={"requests": requests})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
