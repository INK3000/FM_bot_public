from dataclasses import dataclass, fields


@dataclass
class Perfume:
    number: int
    brand: str
    name: str
    description_ru: str
    description_en: str
    description_lt: str
    image_url: str
    image_id: str
    url_ru: str
    url_en: str
    url_lt: str

    def as_list(self):
        return list([getattr(self, f.name) for f in fields(self)])

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
