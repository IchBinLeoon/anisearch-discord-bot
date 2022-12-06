create type application_command_type as enum ('chat_input', 'user', 'message');

create type anime_platform as enum ('anilist', 'myanimelist', 'kitsu');

create table guilds
(
    id       bigint                              not null
        constraint guilds_pk
            primary key,
    added_at timestamp default CURRENT_TIMESTAMP not null
);

create table users
(
    id       bigint                              not null
        constraint users_pk
            primary key,
    added_at timestamp default CURRENT_TIMESTAMP not null
);

create table guild_episode_notifications
(
    guild_id   bigint                              not null
        constraint guild_episode_notifications_guilds_id_fk
            references guilds
            on delete cascade,
    anilist_id integer                             not null,
    title      text                                not null,
    added_at   timestamp default CURRENT_TIMESTAMP not null
);

create unique index guild_episode_notifications_guild_id_anilist_id_uindex
    on guild_episode_notifications (guild_id, anilist_id);

create table guild_channels
(
    guild_id   bigint                              not null
        constraint guild_channels_guilds_id_fk
            references guilds
            on delete cascade,
    channel_id bigint                              not null,
    added_at   timestamp default CURRENT_TIMESTAMP not null
);

create unique index guild_channels_guild_id_uindex
    on guild_channels (guild_id);

create table guild_roles
(
    guild_id bigint                              not null
        constraint guild_roles_guilds_id_fk
            references guilds
            on delete cascade,
    role_id  bigint                              not null,
    added_at timestamp default CURRENT_TIMESTAMP not null
);

create unique index guild_roles_guild_id_uindex
    on guild_roles (guild_id);

create table user_profiles
(
    user_id    bigint                              not null
        constraint user_profiles_users_id_fk
            references users
            on delete cascade,
    platform   anime_platform                      not null,
    profile_id integer                             not null,
    added_at   timestamp default CURRENT_TIMESTAMP not null
);

create unique index user_profiles_user_id_platform_uindex
    on user_profiles (user_id, platform);

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