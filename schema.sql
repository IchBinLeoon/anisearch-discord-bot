create type application_command_type as enum ('chat_input', 'user', 'message');

create type anime_platform as enum ('anilist', 'myanimelist', 'kitsu');

create table guilds
(
    id       bigint                              not null
        constraint guilds_pk
            primary key,
    added_at timestamp default CURRENT_TIMESTAMP not null
);

create table guild_command_usages
(
    shard_id     integer                             not null,
    guild_id     bigint                              not null,
    channel_id   bigint                              not null,
    user_id      bigint                              not null,
    command_name text                                not null,
    command_type application_command_type            not null,
    used_at      timestamp default CURRENT_TIMESTAMP not null
);

create table private_command_usages
(
    user_id      bigint                              not null,
    command_name text                                not null,
    command_type application_command_type            not null,
    used_at      timestamp default CURRENT_TIMESTAMP not null
);

create table user_profiles
(
    user_id  bigint                              not null,
    platform anime_platform                      not null,
    username text                                not null,
    added_at timestamp default CURRENT_TIMESTAMP not null
);

create unique index user_profiles_user_id_platform_uindex
    on user_profiles (user_id, platform);