use std::process::Command;

use chrono::Utc;

fn main() {
    println!(
        "cargo:rustc-env=GIT_COMMIT_HASH={}",
        get_git_commit_hash().unwrap_or_default()
    );

    println!("cargo:rustc-env=BUILD_DATE={}", Utc::now().format("%F"));
}

fn get_git_commit_hash() -> Option<String> {
    let output = Command::new("git")
        .arg("rev-parse")
        .arg("--short")
        .arg("HEAD")
        .output();

    output
        .ok()
        .filter(|o| o.status.success())
        .and_then(|o| {
            String::from_utf8(o.stdout)
                .ok()
                .map(|s| s.trim().to_string())
        })
        .filter(|o| !o.is_empty())
}
