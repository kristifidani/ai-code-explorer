use actix_web::{App, HttpServer};
use backend::{app_config::config_app, tracing::tracing_setup, utils::parse_env_expect};

/// Starts the Actix-web server, initializing environment variables, logging, and application configuration.
///
/// Loads environment variables from a `.env` file, sets up tracing for logging, retrieves the server port from the `APP_PORT` environment variable, and runs the HTTP server bound to all interfaces on the specified port. Returns any I/O errors encountered during server startup or execution.
///
/// # Examples
///
/// ```no_run
/// // Run the server (typically invoked as the application entry point)
/// main().await.unwrap();
/// ```
async fn main() -> std::io::Result<()> {
    dotenvy::dotenv().ok();
    tracing_setup();

    // get port from environment variable
    let port: u16 = parse_env_expect("APP_PORT");

    HttpServer::new(|| {
        App::new()
            .configure(config_app)
            .wrap(actix_web::middleware::Logger::default())
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
