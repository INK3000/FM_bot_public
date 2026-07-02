CREATE SCHEMA IF NOT EXISTS api;

CREATE TABLE IF NOT EXISTS api.users (
    id_telegram BIGINT NOT NULL,
    first_name VARCHAR NULL,
    last_name VARCHAR NULL,
    username VARCHAR NULL,
    language_code VARCHAR NULL,
    refered_by BIGINT NULL,
    is_deleted BOOLEAN DEFAULT false NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id_telegram),
    CONSTRAINT users_refered_by_fkey
        FOREIGN KEY (refered_by)
        REFERENCES api.users(id_telegram)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS api.perfume_preferences (
    user_id BIGINT NOT NULL,
    perfume_id VARCHAR(20) NOT NULL,
    in_wishlist BOOLEAN DEFAULT false NULL,
    in_collection BOOLEAN DEFAULT false NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT user_perfume_unique PRIMARY KEY (user_id, perfume_id),
    CONSTRAINT perfume_preferences_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES api.users(id_telegram)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_perfume_preferences_user_id
    ON api.perfume_preferences(user_id);

CREATE INDEX IF NOT EXISTS idx_perfume_preferences_perfume_id
    ON api.perfume_preferences(perfume_id);

CREATE OR REPLACE FUNCTION api.get_user_with_perfume_preferences_obj(tgid BIGINT)
RETURNS JSONB
LANGUAGE sql
SET search_path TO 'api'
AS $$
    SELECT to_jsonb(u) || jsonb_build_object(
        'preferences_perfume',
        COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'perfume_id', pp.perfume_id,
                    'in_wishlist', pp.in_wishlist,
                    'in_collection', pp.in_collection,
                    'created_at', pp.created_at,
                    'updated_at', pp.updated_at
                )
            ) FILTER (WHERE pp.perfume_id IS NOT NULL),
            '[]'::jsonb
        )
    )
    FROM users u
    LEFT JOIN perfume_preferences pp
        ON u.id_telegram = pp.user_id
    WHERE u.id_telegram = tgid
    GROUP BY u.id_telegram;
$$;

CREATE OR REPLACE FUNCTION api.create_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT '',
    _last_name TEXT DEFAULT '',
    _username TEXT DEFAULT '',
    _language_code TEXT DEFAULT ''
)
RETURNS JSONB
LANGUAGE plpgsql
SET search_path TO 'api'
AS $$
DECLARE
    result JSONB;
BEGIN
    INSERT INTO users (
        id_telegram,
        first_name,
        last_name,
        username,
        language_code,
        is_deleted,
        created_at,
        updated_at
    )
    VALUES (
        _id_telegram,
        _first_name,
        _last_name,
        _username,
        _language_code,
        false,
        now(),
        now()
    )
    ON CONFLICT (id_telegram) DO NOTHING;

    SELECT get_user_with_perfume_preferences_obj(_id_telegram)
    INTO result;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION api.update_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT NULL,
    _last_name TEXT DEFAULT NULL,
    _username TEXT DEFAULT NULL,
    _language_code TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SET search_path TO 'api'
AS $$
DECLARE
    result JSONB;
BEGIN
    UPDATE users
    SET
        first_name = COALESCE(_first_name, first_name),
        last_name = COALESCE(_last_name, last_name),
        username = COALESCE(_username, username),
        language_code = COALESCE(_language_code, language_code),
        updated_at = now()
    WHERE id_telegram = _id_telegram;

    SELECT get_user_with_perfume_preferences_obj(_id_telegram)
    INTO result;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION api.upsert_user(
    _id_telegram BIGINT,
    _first_name TEXT DEFAULT NULL,
    _last_name TEXT DEFAULT NULL,
    _username TEXT DEFAULT NULL,
    _language_code TEXT DEFAULT NULL,
    _refered_by BIGINT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SET search_path TO 'api'
AS $$
DECLARE
    result JSONB;
BEGIN
    INSERT INTO users (
        id_telegram,
        first_name,
        last_name,
        username,
        language_code,
        refered_by,
        is_deleted,
        created_at,
        updated_at
    )
    VALUES (
        _id_telegram,
        COALESCE(_first_name, ''),
        COALESCE(_last_name, ''),
        COALESCE(_username, ''),
        COALESCE(_language_code, ''),
        _refered_by,
        false,
        now(),
        now()
    )
    ON CONFLICT (id_telegram)
    DO UPDATE SET
        first_name = COALESCE(EXCLUDED.first_name, users.first_name),
        last_name = COALESCE(EXCLUDED.last_name, users.last_name),
        username = COALESCE(EXCLUDED.username, users.username),
        language_code = COALESCE(EXCLUDED.language_code, users.language_code),
        refered_by = COALESCE(EXCLUDED.refered_by, users.refered_by),
        updated_at = now();

    SELECT get_user_with_perfume_preferences_obj(_id_telegram)
    INTO result;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION api.upsert_perfume_preference(
    _user_id BIGINT,
    _perfume_id VARCHAR,
    _in_wishlist BOOLEAN DEFAULT NULL,
    _in_collection BOOLEAN DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SET search_path TO 'api'
AS $$
DECLARE
    result JSONB;
BEGIN
    INSERT INTO perfume_preferences (
        user_id,
        perfume_id,
        in_wishlist,
        in_collection,
        created_at,
        updated_at
    )
    VALUES (
        _user_id,
        _perfume_id,
        COALESCE(_in_wishlist, false),
        COALESCE(_in_collection, false),
        now(),
        now()
    )
    ON CONFLICT (user_id, perfume_id)
    DO UPDATE SET
        in_wishlist = COALESCE(_in_wishlist, perfume_preferences.in_wishlist),
        in_collection = COALESCE(_in_collection, perfume_preferences.in_collection),
        updated_at = now();

    SELECT get_user_with_perfume_preferences_obj(_user_id)
    INTO result;

    RETURN result;
END;
$$;
