-- EXTENSIONS
CREATE EXTENSION IF NOT EXISTS vector;

-- SCHEMA: sdk_cache

CREATE SCHEMA IF NOT EXISTS sdk_cache
    AUTHORIZATION cards;

-- Table: sdk_cache.set

CREATE TABLE IF NOT EXISTS sdk_cache.set
(
    id text COLLATE pg_catalog."default" NOT NULL,
    image_uri text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    series text COLLATE pg_catalog."default",
    release_date date,
    CONSTRAINT set_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE sdk_cache.set
    OWNER to cards;

-- Table: sdk_cache.card

CREATE TABLE IF NOT EXISTS sdk_cache.card
(
    id text COLLATE pg_catalog."default" NOT NULL,
    set_id text COLLATE pg_catalog."default",
    image_uri_large text COLLATE pg_catalog."default",
    image_uri_small text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    wishlist_quantity integer DEFAULT 0,
    features vector(4096),
    CONSTRAINT card_pkey PRIMARY KEY (id),
    CONSTRAINT set_id FOREIGN KEY (set_id)
        REFERENCES sdk_cache.set (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE sdk_cache.card
    OWNER to cards;

-- SCHEMA: user_data

CREATE SCHEMA IF NOT EXISTS user_data
    AUTHORIZATION cards;

-- Table: user_data.upload

CREATE TABLE IF NOT EXISTS user_data.upload
(
    image_path text COLLATE pg_catalog."default" NOT NULL,
    id serial NOT NULL,
    CONSTRAINT upload_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS user_data.upload
    OWNER to cards;

-- Table: user_data.match

CREATE TABLE IF NOT EXISTS user_data.match
(
    card_id text COLLATE pg_catalog."default" NOT NULL,
    id serial NOT NULL,
    upload_id serial NOT NULL,
    CONSTRAINT match_pkey PRIMARY KEY (id),
    CONSTRAINT card_id FOREIGN KEY (card_id)
        REFERENCES sdk_cache.card (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT upload_id FOREIGN KEY (upload_id)
        REFERENCES user_data.upload (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS user_data.match
    OWNER to cards;
