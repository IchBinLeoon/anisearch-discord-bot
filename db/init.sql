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
    id bigint,
    time bigint,
    episode int,
    romaji text,
    english text,
    image text,
    url text,
    nsfw boolean
);