use std::sync::Arc;

use anisearch_entity::{guild_command_usages, private_command_usages, users};
use poise::serenity_prelude::{GuildId, UserId};
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, PaginatorTrait, Set};

use crate::utils::commands::{CommandType, ExecutionStatus};

pub struct MetricsService {
    database: Arc<DatabaseConnection>,
}

impl MetricsService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
    }

    pub async fn add_guild_command_usage(
        &self,
        ctx_id: u64,
        user_id: UserId,
        guild_id: GuildId,
        command_name: String,
        command_type: CommandType,
        execution_status: ExecutionStatus,
    ) -> Result<(), DbErr> {
        let model = guild_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            user_id: Set(Some(user_id.get() as i64)),
            guild_id: Set(Some(guild_id.get() as i64)),
            command_name: Set(command_name),
            command_type: Set(command_type.into()),
            execution_status: Set(execution_status.into()),
            ..Default::default()
        };

        guild_command_usages::Entity::insert(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn add_private_command_usage(
        &self,
        ctx_id: u64,
        user_id: UserId,
        command_name: String,
        command_type: CommandType,
        execution_status: ExecutionStatus,
    ) -> Result<(), DbErr> {
        let model = private_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            user_id: Set(Some(user_id.get() as i64)),
            command_name: Set(command_name),
            command_type: Set(command_type.into()),
            execution_status: Set(execution_status.into()),
            ..Default::default()
        };

        private_command_usages::Entity::insert(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn update_guild_command_usage(
        &self,
        ctx_id: u64,
        execution_status: ExecutionStatus,
        execution_time: u128,
    ) -> Result<(), DbErr> {
        let model = guild_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            execution_status: Set(execution_status.into()),
            execution_time: Set(Some(execution_time as i32)),
            ..Default::default()
        };

        guild_command_usages::Entity::update(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn update_private_command_usage(
        &self,
        ctx_id: u64,
        execution_status: ExecutionStatus,
        execution_time: u128,
    ) -> Result<(), DbErr> {
        let model = private_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            execution_status: Set(execution_status.into()),
            execution_time: Set(Some(execution_time as i32)),
            ..Default::default()
        };

        private_command_usages::Entity::update(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn get_user_count(&self) -> Result<u64, DbErr> {
        users::Entity::find().count(self.database.as_ref()).await
    }

    pub async fn get_commands_used_count(&self) -> Result<u64, DbErr> {
        let guild_count = guild_command_usages::Entity::find()
            .count(self.database.as_ref())
            .await?;

        let private_count = private_command_usages::Entity::find()
            .count(self.database.as_ref())
            .await?;

        Ok(guild_count + private_count)
    }
}
