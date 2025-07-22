use actix_web::{App, HttpServer};
use backend::{app_config::config_app, tracing::tracing_setup, utils::parse_env_expect};

#[actix_web::main]
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
