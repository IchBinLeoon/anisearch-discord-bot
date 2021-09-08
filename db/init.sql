CREATE TABLE IF NOT EXISTS guilds (
    id bigint NOT NULL,
    prefix varchar(5) NOT NULL,
    channel bigint,
    role bigint,
    watchlist integer[] NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS users (
    id bigint NOT NULL,
    anilist text,
    myanimelist text,
    kitsu text
);

CREATE TABLE IF NOT EXISTS schedule (
    id bigint NOT NULL,
    time bigint NOT NULL,
    episode int NOT NULL,
    romaji text NOT NULL,
    english text,
    image text NOT NULL,
    url text NOT NULL,
    nsfw boolean NOT NULL
);