class MixinRenameKeys:
    @staticmethod
    def _rename_keys( data):
        return {f"_{key}": value for key, value in data.items()}
