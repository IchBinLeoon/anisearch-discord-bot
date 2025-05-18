use poise::serenity_prelude::Error as SerenityError;
use poise::{CreateReply, FrameworkError};
use sea_orm::DbErr;
use thiserror::Error;
use tracing::error;

use crate::Data;
use crate::utils::embeds::create_error_embed;

pub type Result<T, E = Error> = std::result::Result<T, E>;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Serenity error: {0}")]
    Serenity(#[source] SerenityError),

    #[error("Database error: {0}")]
    Database(#[source] DbErr),
}

impl From<SerenityError> for Error {
    fn from(e: SerenityError) -> Self {
        Self::Serenity(e)
    }
}

impl From<DbErr> for Error {
    fn from(e: DbErr) -> Self {
        Self::Database(e)
    }
}

pub async fn on_error(error: FrameworkError<'_, Data, Error>) -> Result<()> {
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

        ctx.send(reply).await?;
    }

    Ok(())
}
