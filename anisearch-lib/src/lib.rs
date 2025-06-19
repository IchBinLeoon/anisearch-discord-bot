pub mod config;
pub mod database;
pub mod grpc;

pub const BOT_INVITE: &str = "https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=18432&scope=bot%20applications.commands";
pub const SERVER_INVITE: &str = "https://discord.gg/Bv94yQYZM8";
pub const WEBSITE_URL: &str = "https://anisearch.ichbinleoon.dev/";

pub fn version() -> String {
    let cargo_pkg_version = env!("CARGO_PKG_VERSION");
    let git_commit_hash = env!("GIT_COMMIT_HASH");
    let build_date = env!("BUILD_DATE");

    if git_commit_hash.is_empty() {
        cargo_pkg_version.to_string()
    } else {
        format!("{} ({} {})", cargo_pkg_version, git_commit_hash, build_date)
    }
}
