use crate::Context;
use crate::error::Result;

pub async fn defer_with_ephemeral(ctx: Context<'_>, ephemeral: Option<bool>) -> Result<bool> {
    let ephemeral = ephemeral.unwrap_or_default();

    if ephemeral {
        ctx.defer_ephemeral().await?;
    } else {
        ctx.defer().await?;
    }

    Ok(ephemeral)
}
