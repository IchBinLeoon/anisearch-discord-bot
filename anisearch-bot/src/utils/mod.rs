pub mod embeds;

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
