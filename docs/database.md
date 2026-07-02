# Database

This document describes the PostgreSQL database used by the Telegram bot.

## Database Schema

The project uses the `api` schema.

### Tables

#### `api.users`

Stores Telegram user information.

| Column | Type | Description |
|---|---|---|
| `id_telegram` | `BIGINT` | Primary key. Telegram user ID. |
| `first_name` | `VARCHAR` | Telegram first name. |
| `last_name` | `VARCHAR` | Telegram last name. |
| `username` | `VARCHAR` | Telegram username. |
| `language_code` | `VARCHAR` | Selected or detected language code. |
| `refered_by` | `BIGINT` | Optional Telegram user ID of the referring user. |
| `is_deleted` | `BOOLEAN` | Soft-delete flag. |
| `created_at` | `TIMESTAMPTZ` | Record creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` | Last update timestamp. |

Primary key:

```sql
PRIMARY KEY (id_telegram)
```

Foreign keys:

```sql
FOREIGN KEY (refered_by)
REFERENCES api.users(id_telegram)
ON DELETE SET NULL
```

#### `api.perfume_preferences`

Stores user-specific perfume preferences.

A single row represents one user's relationship to one perfume.

| Column | Type | Description |
|---|---|---|
| `user_id` | `BIGINT` | Telegram user ID. Foreign key to `api.users(id_telegram)`. |
| `perfume_id` | `VARCHAR(20)` | Perfume identifier from the catalogue/search index. |
| `in_wishlist` | `BOOLEAN` | Whether the perfume is in the user's wishlist. |
| `in_collection` | `BOOLEAN` | Whether the perfume is in the user's collection. |
| `created_at` | `TIMESTAMPTZ` | Record creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` | Last update timestamp. |

Primary key:

```sql
PRIMARY KEY (user_id, perfume_id)
```

Foreign keys:

```sql
FOREIGN KEY (user_id)
REFERENCES api.users(id_telegram)
ON DELETE CASCADE
```

Indexes:

```sql
CREATE INDEX idx_perfume_preferences_user_id
    ON api.perfume_preferences(user_id);

CREATE INDEX idx_perfume_preferences_perfume_id
    ON api.perfume_preferences(perfume_id);
```

## Stored Functions

The application interacts with the database primarily through PostgreSQL stored functions. This keeps user upsert and preference update logic close to the data layer.

### `api.create_user`

Creates a user if it does not already exist and returns the user object with perfume preferences.

```sql
api.create_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT '',
    _last_name TEXT DEFAULT '',
    _username TEXT DEFAULT '',
    _language_code TEXT DEFAULT ''
) RETURNS JSONB
```

### `api.update_user`

Updates an existing user and returns the user object with perfume preferences.

```sql
api.update_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT NULL,
    _last_name TEXT DEFAULT NULL,
    _username TEXT DEFAULT NULL,
    _language_code TEXT DEFAULT NULL
) RETURNS JSONB
```

### `api.upsert_user`

Creates or updates a user and returns the user object with perfume preferences.

```sql
api.upsert_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT NULL,
    _last_name TEXT DEFAULT NULL,
    _username TEXT DEFAULT NULL,
    _language_code TEXT DEFAULT NULL,
    _refered_by BIGINT DEFAULT NULL
) RETURNS JSONB
```

### `api.upsert_perfume_preference`

Creates or updates a perfume preference row for a user.

The function supports partial updates: if one of the boolean values is passed as `NULL`, the existing value is preserved.

```sql
api.upsert_perfume_preference(
    _user_id BIGINT,
    _perfume_id VARCHAR,
    _in_wishlist BOOLEAN DEFAULT NULL,
    _in_collection BOOLEAN DEFAULT NULL
) RETURNS JSONB
```

### `api.get_user_with_perfume_preferences_obj`

Returns a user object together with the user's perfume preferences.

```sql
api.get_user_with_perfume_preferences_obj(
    tgid BIGINT
) RETURNS JSONB
```

The returned JSON contains user fields and a `preferences_perfume` array.

## Migrations

The project uses plain SQL migration files instead of a migration framework.

Migration files are stored in `bot/app/migrations/`.

Current migrations:

| File | Description |
|---|---|
| `bot/app/migrations/001_initial.sql` | Creates the initial schema, tables, indexes, constraints and stored functions. |

New database changes should be added as new migration files instead of editing already applied migrations.

Example naming pattern:

```text
bot/app/migrations/
├── 001_initial.sql
├── 002_add_new_index.sql
└── 003_add_new_table.sql
```

## Initialize the Database

The project uses a containerized PostgreSQL setup.

Once the PostgreSQL container is running, initialize the schema with:

```bash
podman exec -i fm_db \
  psql -U myuser -d mydb \
  < bot/app/migrations/001_initial.sql
```

This command applies the initial schema to the running `fm_db` container.

## Connection Configuration

The bot reads PostgreSQL connection settings from environment variables.

Expected variables:

```env
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=<database_password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

Inside the container network, the bot connects to PostgreSQL through the service name defined in the compose file.

Example DSN built by the application:

```text
postgresql://myuser:<database_password>@postgres:5432/mydb
```

## Connection Pool

The bot creates an `asyncpg` connection pool during startup and passes it into handlers through aiogram dependency injection.

Simplified flow:

```python
async with asyncpg.create_pool(settings.db.dsn) as pool:
    await dp.start_polling(
        bot,
        connection=pool,
        algolia_client=algolia_client,
    )
```

Handlers and middleware receive the pool as `connection` and use it through the repository/service layer.

## Backup and Restore

The project includes admin-only backup and restore commands in the Telegram bot.

### Backup

The `/backup` command creates a SQL dump using `pg_dump` and sends it to the admin as a Telegram document.

The backup process uses the current PostgreSQL DSN from application settings.

### Restore

The `/restore` flow allows an admin to upload a `.sql` file and restore it through `psql`.

Restore is protected by admin ID checks and confirmation flow inside the bot.

### Manual Container Backup

A manual backup can also be created from the running container:

```bash
podman exec fm_db \
  pg_dump -U myuser -d mydb -f - \
  > fm_backup.sql
```

### Manual Container Restore

A manual SQL restore can be executed with:

```bash
podman exec -i fm_db \
  psql -U myuser -d mydb \
  < fm_backup.sql
```

## Security Notes

The database stores only bot-related user data and perfume preference flags.

Sensitive configuration values must be provided through environment variables and must not be committed to the repository.

Database dumps may contain real Telegram user IDs, names and usernames. Backup files should not be committed to Git.
