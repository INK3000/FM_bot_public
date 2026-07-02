from ..repos.mixin_rename_keys import MixinRenameKeys
from ..services.service_protocol import ServiceProtocol
from ..structs.user import User


class UserRepository(MixinRenameKeys):
    def __init__(self, service: ServiceProtocol):
        self._service: ServiceProtocol = service

    async def create_or_update(self, data):
        data = self._rename_keys(data)
        response = await self._service.upsert_user(data)
        user = User.from_json(response)
        return user
    
    async def update_perfume_preferences(self, data):
        data = self._rename_keys(data)
        response = await self._service.upsert_perfume_preference(data)
        user = User.from_json(response)
        return user
