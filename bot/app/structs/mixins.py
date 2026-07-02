import msgspec


class EncodeMethod:
    def to_json(self):
        '''
        Encode object to json
        '''
        return msgspec.json.encode(self)


class DecodeMethod:
    @classmethod
    def from_json(cls, data):
        '''
        Class method allows to decode json to object
        exapmle:
            user = User.from_json(response.content)
        '''
        return msgspec.json.decode(data, type=cls, strict=False)


class AsDictMethod:
    def as_dict(self):
        '''
        Return object as dict
        '''
        fields = getattr(self, "__struct_fields__", ())
        return {f: getattr(self, f) for f in fields}
