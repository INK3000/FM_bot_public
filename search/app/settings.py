from dataclasses import dataclass

from environs import Env


@dataclass
class Settings:
    algolia_app_id: str
    algolia_backend_api_key: str
    algolia_index_name: str
    google_sheet_id: str
    google_wks_id: int

def validate_if_not_set(variable):
    return bool(len(str(variable)))

def validate_if_is_int(variable):
    return isinstance(variable, int)

def get_settings():
    env = Env(eager=False)
    env.read_env()
    settings = Settings(
        algolia_app_id=env.str('ALGOLIA_APP_ID', validate=validate_if_not_set),
        algolia_backend_api_key=env.str('ALGOLIA_BACKEND_API_KEY', validate=validate_if_not_set),
        algolia_index_name=env.str('ALGOLIA_INDEX_NAME', validate=validate_if_not_set),
        google_sheet_id=env.str('GOOGLE_SPREADSHEET_ID', validate=validate_if_not_set),
        google_wks_id=env.int('GOOGLE_WORKSHEET_ID', validate=[validate_if_not_set, validate_if_is_int]),
    )
    env.seal()
    return settings

settings = get_settings()


