use std::error::Error;
use std::process::Command;

use chrono::Utc;
use tonic_prost_build::configure;

fn main() -> Result<(), Box<dyn Error>> {
    configure()
        .type_attribute(".", "#[derive(serde::Serialize, serde::Deserialize)]")
        .compile_protos(&["proto/bot.proto"], &["proto"])?;

    println!(
        "cargo:rustc-env=GIT_COMMIT_HASH={}",
        get_git_commit_hash().unwrap_or_default()
    );

    println!("cargo:rustc-env=BUILD_DATE={}", Utc::now().format("%F"));

    Ok(())
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
