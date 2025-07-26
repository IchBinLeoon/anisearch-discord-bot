use chrono::NaiveDate;
use once_cell::sync::Lazy;
use poise::serenity_prelude::Color;
use regex::Regex;

pub static UNKNOWN_EMBED_FIELD: &str = "Unknown";

static CLEAN_HTML_RE: Lazy<Regex> = Lazy::new(|| Regex::new(r"<.*?>").unwrap());

fn clean_html(text: &str) -> String {
    CLEAN_HTML_RE.replace_all(text, "").to_string()
}

pub fn sanitize_description(description: &str, length: usize) -> String {
    let mut sanitized = clean_html(description)
        .replace("**", "")
        .replace("__", "")
        .replace("~!", "||")
        .replace("!~", "||");

    if sanitized.len() > length {
        sanitized = sanitized.chars().take(length).collect();

        if sanitized.matches("||").count() % 2 != 0 {
            return format!("{sanitized}...||");
        }

        return format!("{sanitized}...");
    }

    sanitized
}

pub fn convert_to_color(color: &str) -> Option<Color> {
    if let Ok(value) = u32::from_str_radix(color.strip_prefix("#")?, 16) {
        Some(Color::from(value))
    } else {
        None
    }
}

pub fn format_opt<T: ToString>(value: Option<T>) -> String {
    value.map_or(UNKNOWN_EMBED_FIELD.to_string(), |v| v.to_string())
}

fn date_with_fallback(year: i64, month: i64, day: i64, fmt: &str) -> String {
    NaiveDate::from_ymd_opt(year as i32, month as u32, day as u32)
        .map(|date| date.format(fmt).to_string())
        .unwrap_or(UNKNOWN_EMBED_FIELD.to_string())
}

pub fn format_date(year: Option<i64>, month: Option<i64>, day: Option<i64>) -> String {
    match (year, month, day) {
        (Some(y), Some(m), Some(d)) => date_with_fallback(y, m, d, "%b %d, %Y"),
        (Some(y), Some(m), None) => date_with_fallback(y, m, 1, "%b, %Y"),
        (Some(y), None, None) => y.to_string(),
        (None, Some(m), Some(d)) => date_with_fallback(0, m, d, "%b %d"),
        _ => UNKNOWN_EMBED_FIELD.to_string(),
    }
}
