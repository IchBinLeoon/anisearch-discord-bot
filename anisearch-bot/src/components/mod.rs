use poise::serenity_prelude::Error as SerenityError;
use thiserror::Error;
use tokio::sync::mpsc::error::SendError;
use tokio::task::JoinError;

pub mod paginate;

#[derive(Error, Debug)]
pub enum ComponentError {
    #[error(transparent)]
    Serenity(#[from] SerenityError),

    #[error(transparent)]
    Join(#[from] JoinError),

    #[error("{0}")]
    Send(String),
}

impl<T> From<SendError<T>> for ComponentError {
    fn from(e: SendError<T>) -> Self {
        ComponentError::Send(e.to_string())
    }
}
