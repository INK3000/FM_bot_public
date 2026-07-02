# Telegram Bot

The `bot` module contains the aiogram-based Telegram bot. It searches perfumes through Algolia and stores user language, wishlist and collection preferences in PostgreSQL.

## Overview

Current bot functionality:

- exact perfume lookup by Algolia `objectID`
- text search by brand, name or query through Algolia
- wishlist and collection toggles through inline callbacks
- `/wishlist` and `/collection` list views
- language selection for English, Russian and Lithuanian
- user upsert and FSM cache through middleware
- admin-only cache clearing
- admin-only PostgreSQL backup and restore
- APScheduler startup for background jobs

## Module Structure

```text
bot/
├── __main__.py
├── Dockerfile
├── requirements.txt
└── app/
    ├── handlers/
    ├── keyboards/
    ├── middlewares/
    ├── migrations/
    ├── misc/
    ├── repos/
    ├── scheduler/
    ├── services/
    ├── states/
    ├── structs/
    └── strings.py
```

## Entry Point

File: `bot/__main__.py`

Startup flow:

1. Configures logging from `DEBUG`.
2. Creates an aiogram `Bot` with HTML parse mode.
3. Registers public Telegram commands from `get_bot_commands()`.
4. Creates a `Dispatcher`.
5. Registers startup and shutdown hooks.
6. Includes routers for commands, backup/restore, text search and preference callbacks.
7. Adds chat-action and user middleware.
8. Deletes pending webhooks.
9. Starts APScheduler.
10. Opens an `asyncpg` pool and an async Algolia client.
11. Starts long polling with `connection` and `algolia_client` injected into handlers.

Simplified shape:

```python
async with asyncpg.create_pool(settings.db.dsn) as pool:
    async with AlgoliaClient(settings) as algolia_client:
        await dp.start_polling(
            bot,
            connection=pool,
            algolia_client=algolia_client,
        )
```

## Configuration

File: `bot/app/settings.py`

Settings are loaded with `environs`. `env.seal()` is used, so unexpected environment variables may fail settings loading.

| Variable | Required | Notes |
|---|---:|---|
| `DEBUG` | No | Enables debug logging. |
| `IS_DEVELOPMENT` | No | Uses `BOT_TOKEN_DEV` when true. |
| `BOT_TOKEN` | Yes | Production bot token. |
| `BOT_TOKEN_DEV` | When `IS_DEVELOPMENT=true` | Development bot token. |
| `BOT_ADMINS` | No | Comma-separated admin Telegram IDs. Defaults to an empty list. |
| `SENTRY_DSN` | No | Optional Sentry DSN. Sentry is disabled when empty. |
| `ALGOLIA_APP_ID` | Yes | Algolia app ID. |
| `ALGOLIA_BACKEND_API_KEY` | Yes | Algolia key used by the bot. |
| `ALGOLIA_INDEX_NAME` | Yes | Algolia index name. |
| `POSTGRES_DB` | Yes | Database name. |
| `POSTGRES_USER` | Yes | Database user. |
| `POSTGRES_PASSWORD` | Yes | Database password. |
| `POSTGRES_HOST` | Yes | Database host. |
| `POSTGRES_PORT` | Yes | Database port. |
| `SCHEDULER_DB_PATH` | No | Optional APScheduler SQLite job store path. Defaults to `/tmp/fm_jobs.sqlite`. |

The PostgreSQL DSN is built as:

```text
postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}
```

## Commands

Public commands returned by `bot/app/misc/bot.py`:

| Command | Handler | Description |
|---|---|---|
| `/start` | `cmd_start.py` | Opens language selection. |
| `/language` | `cmd_language.py` | Lets the user choose English, Lithuanian or Russian. |
| `/wishlist` | `cmd_show_wishlist.py` | Shows perfumes with `in_wishlist=true`. |
| `/collection` | `cmd_show_collection.py` | Shows perfumes with `in_collection=true`. |

Additional admin-only handlers:

| Command | Handler | Description |
|---|---|---|
| `/clear_cache` | `cmd_clear_cache.py` | Clears the middleware user ID cache. |
| `/backup` | `cmd_backup_restore.py` | Dumps PostgreSQL with `pg_dump` and sends the SQL file to the admin. |
| `/restore` | `cmd_backup_restore.py` | Accepts a `.sql` file up to 20 MiB, asks for confirmation and restores with `psql`. |

`/backup` and `/restore` are registered by text matching and are restricted to IDs in `settings.bot.admins`. They are not currently listed in the public Telegram command menu.

## Search Flow

File: `bot/app/handlers/ech_perfume.py`

Text messages are handled as perfume queries:

1. The handler rejects messages longer than 50 characters.
2. It first tries `AlgoliaClient.get_object(text)`, treating the message as an exact object ID.
3. If Algolia raises `RequestException`, it runs `AlgoliaClient.search(query=text)`.
4. Exact matches are shown with localized description and URL fields.
5. Search results are returned as chunks of up to 30 links.
6. If there are no hits, the bot sends the localized "not found" message.

Relevant Algolia fields:

```python
{
    "objectID": "557",
    "brand": "Narciso Rodriguez",
    "name": "Essence",
    "description_en": "...",
    "description_ru": "...",
    "description_lt": "...",
    "url_en": "...",
    "url_ru": "...",
    "url_lt": "...",
    "image_id": "...",
}
```

## Preference Management

File: `bot/app/handlers/perf_preferences.py`

Inline keyboard callbacks contain wishlist/collection actions. The handler:

1. Parses callback data with `prepare_data()`.
2. Calls `UserRepository.update_perfume_preferences()`.
3. Stores the returned user object in FSM state.
4. Rebuilds the inline keyboard for the updated perfume flags.
5. Edits the existing message with the same text and updated buttons.

Preferences are stored in `api.perfume_preferences` with one row per `(user_id, perfume_id)`.

## User Middleware

File: `bot/app/middlewares/users.py`

`UsersAPIMiddleware` runs for messages and callback queries. It:

- reads the current `asyncpg` pool from injected handler data as `connection`
- creates a `UserRepository(PostgresService(connection))`
- clears its in-memory ID cache when the `clear_cache` flag is present
- upserts the Telegram user through PostgreSQL functions when the user is not in state/cache
- stores the returned `User` object in FSM state

The cache stores Telegram IDs only:

```python
cached_users_id: set[int] = set()
```

## Database Access

The supported production runtime uses PostgreSQL stored functions through `PostgresService`:

- `api.upsert_user`
- `api.upsert_perfume_preference`

The repository converts between handler dictionaries and database function argument names, then parses returned JSON into `User`.

## Backup And Restore

Files:

- `bot/app/handlers/cmd_backup_restore.py`
- `bot/app/misc/pg_backup.py`

Backup:

- admin sends `/backup`
- bot runs `pg_dump --clean --if-exists`
- dump is written to `/tmp/fm_backup_<timestamp>.sql`
- file is sent as a Telegram document
- temporary file is removed

Restore:

- admin sends `/restore`
- bot waits for a `.sql` document no larger than 20 MiB
- bot asks for confirmation
- confirmed restore runs `psql -v ON_ERROR_STOP=1 -f <file>`
- user middleware cache is cleared after successful restore
- temporary file is removed

The bot runtime must have `pg_dump` and `psql` installed and available in `PATH`.

## Running

Local run:

```bash
python -m bot
```

Container run:

```bash
podman-compose -f podman-compose.yml up --build --remove-orphans
```
