import importlib
import sys


def _load_settings(monkeypatch, **overrides):
    for key in (
        "BOT_TOKEN",
        "BOT_TOKEN_DEV",
        "IS_DEVELOPMENT",
        "BOT_ADMINS",
        "DEBUG",
        "ALGOLIA_APP_ID",
        "ALGOLIA_BACKEND_API_KEY",
        "ALGOLIA_INDEX_NAME",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "SENTRY_DSN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "API_UPSERT_USER",
        "API_UPSERT_PERFUME_PREFERENCES",
    ):
        monkeypatch.delenv(key, raising=False)

    env = {
        "BOT_TOKEN": "prod-token",
        "BOT_TOKEN_DEV": "dev-token",
        "IS_DEVELOPMENT": "false",
        "BOT_ADMINS": "101,202",
        "DEBUG": "false",
        "ALGOLIA_APP_ID": "algolia-app",
        "ALGOLIA_BACKEND_API_KEY": "algolia-key",
        "ALGOLIA_INDEX_NAME": "perfumes",
        "POSTGRES_DB": "fm",
        "POSTGRES_USER": "fm",
        "POSTGRES_PASSWORD": "secret",
        "POSTGRES_HOST": "postgres",
        "POSTGRES_PORT": "5432",
        "SENTRY_DSN": "",
    }
    env.update(overrides)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    sys.modules.pop("bot.app.settings", None)
    sys.modules.pop("bot", None)
    return importlib.import_module("bot.app.settings").get_settings()


def test_settings_load_postgres_without_legacy_supabase(monkeypatch):
    settings = _load_settings(monkeypatch)

    assert settings.bot.token == "prod-token"
    assert settings.bot.admins == [101, 202]
    assert settings.algolia_search.algolia_index_name == "perfumes"
    assert settings.db.dsn == "postgresql://fm:secret@postgres:5432/fm"
    assert settings.sentry_dsn is None
    assert not hasattr(settings, "supabase")
    assert not hasattr(settings, "api")


def test_settings_use_development_token_and_optional_sentry(monkeypatch):
    settings = _load_settings(
        monkeypatch,
        IS_DEVELOPMENT="true",
        SENTRY_DSN="https://example.invalid/sentry",
    )

    assert settings.bot.token == "dev-token"
    assert settings.sentry_dsn == "https://example.invalid/sentry"
