from msgspec import Struct

from .mixins import AsDictMethod, DecodeMethod, EncodeMethod


class PerfumePreferences(Struct, EncodeMethod, DecodeMethod, AsDictMethod):
    perfume_id: str
    in_wishlist: bool
    in_collection: bool

    def __repr__(self):
        return f'PerfumePreferences({self.perfume_id=}, {self.in_wishlist=}, {self.in_collection=})'

class User(Struct, EncodeMethod, DecodeMethod, AsDictMethod):
    id_telegram: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    preferences_perfume: list[PerfumePreferences]

    def __repr__(self):
        return f'User(id_telegram={self.id_telegram}, username={self.username}, first_name={self.first_name}, last_name={self.last_name}, language_code={self.language_code})'
