//! Small helpers: JSON number extraction from `reference.json` (no serde), formatting.

/// Extract the first number following `"key":` (searching from `from`), or `None`.
pub fn json_f64(text: &str, key: &str) -> Option<f64> {
    json_f64_from(text, key, 0)
}

pub fn json_f64_from(text: &str, key: &str, from: usize) -> Option<f64> {
    let pat = format!("\"{}\"", key);
    let i = text[from..].find(&pat)? + from + pat.len();
    let rest = text[i..].trim_start();
    let rest = rest.strip_prefix(':')?.trim_start();
    let rest = rest.strip_prefix('"').unwrap_or(rest); // numbers stored as strings (mpmath output)
    let end = rest
        .find(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-' || c == '+' || c == 'e' || c == 'E'))
        .unwrap_or(rest.len());
    rest[..end].parse::<f64>().ok()
}

/// Position just after `"key"` (to search a nested object), or `None`.
pub fn json_pos(text: &str, key: &str) -> Option<usize> {
    let pat = format!("\"{}\"", key);
    text.find(&pat).map(|i| i + pat.len())
}

pub fn rel_err(a: f64, b: f64) -> f64 {
    (a - b).abs() / b.abs().max(1e-300)
}
