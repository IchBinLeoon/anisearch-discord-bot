create type application_command_type as enum ('chat_input', 'user', 'message');

create table guilds
(
    id        bigint                              not null
        constraint guilds_pk
            primary key,
    joined_at timestamp default CURRENT_TIMESTAMP not null
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