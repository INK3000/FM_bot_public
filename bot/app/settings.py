from dataclasses import dataclass

from environs import Env


@dataclass
class Bot:
    token: str
    admins: list[int]


@dataclass
class AlgoliaSearch:
    algolia_app_id: str
    algolia_backend_api_key: str
    algolia_index_name: str


@dataclass
class Db:
    dsn: str


@dataclass
class Settings:
    debug: bool
    bot: Bot
    algolia_search: AlgoliaSearch
    db: Db
    sentry_dsn: str | None


def validate_if_not_set(variable) -> bool:
    return bool(len(str(variable)))


def get_settings() -> Settings:
    env = Env(eager=False)
    env.read_env()
    if env.bool("IS_DEVELOPMENT", default=False):
        bot_token = env.str("BOT_TOKEN_DEV", validate=validate_if_not_set)
    else:
        bot_token = env.str("BOT_TOKEN", validate=validate_if_not_set)
    sentry_dsn = env.str("SENTRY_DSN", default=None) or None

    postgres_host = env.str("POSTGRES_HOST", validate=validate_if_not_set)
    postgres_port = env.str("POSTGRES_PORT", validate=validate_if_not_set)
    postgres_user = env.str("POSTGRES_USER", validate=validate_if_not_set)
    postgres_password = env.str("POSTGRES_PASSWORD", validate=validate_if_not_set)
    postgres_db = env.str("POSTGRES_DB", validate=validate_if_not_set)

    postgres_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    settings = Settings(
        debug=env.bool("DEBUG", default=False),
        bot=Bot(
            token=bot_token,
            admins=env.list("BOT_ADMINS", subcast=int, default=[]),
        ),
        algolia_search=AlgoliaSearch(
            algolia_app_id=env.str("ALGOLIA_APP_ID", validate=validate_if_not_set),
            algolia_backend_api_key=env.str("ALGOLIA_BACKEND_API_KEY", validate=validate_if_not_set),
            algolia_index_name=env.str("ALGOLIA_INDEX_NAME", validate=validate_if_not_set),
        ),
        db=Db(dsn=postgres_url),
        sentry_dsn=sentry_dsn,
    )
    env.seal()
    return settings


settings = get_settings()
