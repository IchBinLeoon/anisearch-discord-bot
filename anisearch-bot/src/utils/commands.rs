use std::fmt;

use anisearch_entity::sea_orm_active_enums;
use poise::serenity_prelude::CommandType as SerenityCommandType;

use crate::Context;
use crate::error::Result;

pub struct CommandType(pub SerenityCommandType);

impl fmt::Display for CommandType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.0 {
            SerenityCommandType::ChatInput => write!(f, "CHAT_INPUT"),
            SerenityCommandType::User => write!(f, "USER"),
            SerenityCommandType::Message => write!(f, "MESSAGE"),
            _ => unreachable!(),
        }
    }
}

impl From<CommandType> for sea_orm_active_enums::CommandType {
    fn from(value: CommandType) -> Self {
        match value.0 {
            SerenityCommandType::ChatInput => sea_orm_active_enums::CommandType::ChatInput,
            SerenityCommandType::User => sea_orm_active_enums::CommandType::User,
            SerenityCommandType::Message => sea_orm_active_enums::CommandType::Message,
            _ => unreachable!(),
        }
    }
}

pub enum ExecutionStatus {
    Running,
    Success,
    Error,
}

impl fmt::Display for ExecutionStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ExecutionStatus::Running => write!(f, "RUNNING"),
            ExecutionStatus::Success => write!(f, "SUCCESS"),
            ExecutionStatus::Error => write!(f, "ERROR"),
        }
    }
}

impl From<ExecutionStatus> for sea_orm_active_enums::ExecutionStatus {
    fn from(value: ExecutionStatus) -> Self {
        match value {
            ExecutionStatus::Running => sea_orm_active_enums::ExecutionStatus::Running,
            ExecutionStatus::Success => sea_orm_active_enums::ExecutionStatus::Success,
            ExecutionStatus::Error => sea_orm_active_enums::ExecutionStatus::Error,
        }
    }
}

pub async fn defer_with_ephemeral<'a>(ctx: Context<'a>, ephemeral: Option<bool>) -> Result<bool> {
    let ephemeral = ephemeral.unwrap_or_default();

    if ephemeral {
        ctx.defer_ephemeral().await?;
    } else {
        ctx.defer().await?;
    }

    Ok(ephemeral)
}
