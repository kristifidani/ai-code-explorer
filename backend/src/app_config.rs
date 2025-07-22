use crate::error::Result;
use actix_web::{HttpRequest, HttpResponse, Responder, web};

pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(web::resource("/health").route(web::get().to(health_check)));
}

pub async fn health_check(_: HttpRequest) -> Result<impl Responder> {
    tracing::debug!("Health check!");
    Ok(HttpResponse::Ok().body("API is healthy ✅"))
}
