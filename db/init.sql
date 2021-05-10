CREATE TABLE IF NOT EXISTS guilds (id bigint, prefix VARCHAR (5), channel bigint);
CREATE TABLE IF NOT EXISTS users (id bigint, anilist VARCHAR (255), myanimelist VARCHAR (255), kitsu VARCHAR (255));
CREATE TABLE IF NOT EXISTS schedule (id bigint, time bigint, episode int, romaji VARCHAR (255), english VARCHAR (255), image VARCHAR (255), url VARCHAR (255), nsfw boolean);