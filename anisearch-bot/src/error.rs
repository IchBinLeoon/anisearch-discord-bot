use poise::serenity_prelude::Error as SerenityError;
use poise::{CreateReply, FrameworkError};
use sea_orm::DbErr;
use thiserror::Error;
use tracing::error;

use crate::Data;
use crate::clients::anilist::error::AniListError;
use crate::components::ComponentError;
use crate::events::{ExecutionStatus, log_command_completion};
use crate::utils::embeds::create_error_embed;

pub type Result<T, E = Error> = std::result::Result<T, E>;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Serenity: {0}")]
    Serenity(#[from] SerenityError),

    #[error("Component: {0}")]
    Component(#[from] ComponentError),

    #[error("Database: {0}")]
    Database(#[from] DbErr),

    #[error("AniList: {0}")]
    AniList(#[from] AniListError),
}

pub async fn on_error(error: FrameworkError<'_, Data, Error>) {
    if let FrameworkError::Command { error, .. } = &error {
        error!("An error occurred while executing a command: {error}");
    } else {
        error!("An error occurred: {error}");
    }

    if let Some(ctx) = error.ctx() {
        let embed = create_error_embed(ctx)
            .await
            .title("💢 Command Error")
            .description("An unknown error occurred. Please try again in a moment.");

        let reply = CreateReply::new().embed(embed);

        if let Err(e) = ctx.send(reply).await {
            error!("Failed to send error message: {e}");
        }

        log_command_completion(ctx, ExecutionStatus::Error).await;
    }
}
