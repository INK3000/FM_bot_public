# Federico Mahora Perfume Bot

Telegram bot for finding fragrance references by Federico Mahora code, brand, name or text query. Users can save perfumes to a wishlist or collection. The bot UI supports English, Russian and Lithuanian.

This is a real production bot that has been running for several years.

## Links

- Live Telegram bot: [@FedericoMahoraBot](https://t.me/FedericoMahoraBot)
- Official Federico Mahora website: <https://shop-lt.fmworld.com/>
- Project documentation: [docs/README.md](docs/README.md)

The supported runtime path is:

- Telegram bot: aiogram 3
- Database: PostgreSQL 16
- Search: Algolia
- Containers: Podman Compose

Catalogue data is maintained separately in Google Sheets and indexed into Algolia. The primary runnable application is the Telegram bot.

## Project Structure

```text
FM/
├── bot/                    # aiogram Telegram bot
│   ├── app/
│   │   ├── handlers/        # Commands, text search, callbacks
│   │   ├── migrations/      # PostgreSQL schema and functions
│   │   ├── misc/            # Algolia client, backup helpers, utilities
│   │   ├── repos/           # Repository layer
│   │   ├── services/        # PostgreSQL service layer
│   │   └── strings.py       # Multilingual bot strings
│   ├── Dockerfile
│   └── requirements.txt
├── search/                  # Google Sheets to Algolia indexing
├── docs/                    # Extended documentation
├── podman-compose.yml
├── pyproject.toml
└── uv.lock
```

## Requirements

- Python 3.12+
- Podman and podman-compose
- Telegram bot token
- Algolia application ID, API key and index name

For local Python checks, install dependencies with `uv`.

## Configuration

Copy the committed environment template:

```bash
cp bot/app/.env.dist bot/app/.env
```

Fill in:

```env
BOT_TOKEN=
BOT_TOKEN_DEV=
IS_DEVELOPMENT=false
BOT_ADMINS=
DEBUG=false

ALGOLIA_APP_ID=
ALGOLIA_BACKEND_API_KEY=
ALGOLIA_INDEX_NAME=

POSTGRES_DB=fm
POSTGRES_USER=fm
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

SENTRY_DSN=
SCHEDULER_DB_PATH=/tmp/fm_jobs.sqlite
```

`SENTRY_DSN` is optional. If it is empty, Sentry is not initialized.

## Run With Podman

Create the external network once:

```bash
podman network create \
  --subnet 10.89.0.0/16 \
  --gateway 10.89.0.1 \
  --dns 9.9.9.9 \
  --dns 1.1.1.1 \
  fm-network
```

Start the bot and PostgreSQL:

```bash
podman-compose -f podman-compose.yml up --build
```

PostgreSQL initializes from `bot/app/migrations/001_initial.sql` on the first database volume creation.

## Bot Commands

Public commands:

- `/start`
- `/language`
- `/wishlist`
- `/collection`

Admin-only text commands for IDs listed in `BOT_ADMINS`:

- `/clear_cache`
- `/backup`
- `/restore`

Backup and restore use `pg_dump` and `psql` inside the bot container.

## Development Checks

Install dependencies:

```bash
uv sync
```

Run checks:

```bash
uv run ruff check .
uv run basedpyright
uv run pytest
```

## Maintenance Tools

Index Google Sheets data into Algolia:

```bash
python -m search
```
