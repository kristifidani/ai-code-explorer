use actix_web::{HttpRequest, HttpResponse, Responder, web};

/// Configures the Actix-web application with the health check endpoint.
///
/// Registers a GET route at `/health` that responds with the application's health status.
///
/// # Examples
///
/// ```
/// let mut cfg = actix_web::web::ServiceConfig::new();
/// config_app(&mut cfg);
/// // The application now serves GET /health
/// ```
pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(web::resource("/health").route(web::get().to(health_check)));
}

/// Handles health check requests and returns a 200 OK response indicating the API is healthy.
///
/// # Examples
///
/// ```
/// use actix_web::{test, App};
/// use backend::app_config::health_check;
///
/// let app = test::init_service(App::new().route("/health", actix_web::web::get().to(health_check))).await;
/// let req = test::TestRequest::get().uri("/health").to_request();
/// let resp = test::call_service(&app, req).await;
/// assert_eq!(resp.status(), actix_web::http::StatusCode::OK);
/// ```
pub async fn health_check(_: HttpRequest) -> impl Responder {
    tracing::debug!("Health check!");
    HttpResponse::Ok().body("API is healthy ✅")
}
