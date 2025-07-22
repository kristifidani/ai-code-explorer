use std::str::FromStr;

/// Loads an environment variable by key and parses its value into the specified type.
///
/// Panics if the environment variable is missing or if parsing fails, providing detailed error messages.
///
/// # Examples
///
/// ```
/// use your_crate::parse_env_expect;
/// std::env::set_var("PORT", "8080");
/// let port: u16 = parse_env_expect("PORT");
/// assert_eq!(port, 8080);
/// ```
pub fn parse_env_expect<T: FromStr<Err = E>, E: std::fmt::Display>(key: &str) -> T {
    let value = std::env::var(key).unwrap_or_else(|_| {
        let msg = format!("Environment variable {key} not set. {key} must be set!");
        tracing::error!("{msg}");
        panic!("{msg}")
    });

    value.parse().unwrap_or_else(|e| {
        let msg = format!(
            "Failed to parse value '{value}' from {key} into '{}': {e}",
            std::any::type_name::<T>()
        );
        tracing::error!("{msg}");
        panic!("{msg}")
    })
}
