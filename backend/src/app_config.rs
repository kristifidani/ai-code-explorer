use actix_web::{HttpRequest, HttpResponse, Responder, web};

pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(web::resource("/health").route(web::get().to(health_check)));
}

pub async fn health_check(_: HttpRequest) -> impl Responder {
    tracing::debug!("Health check!");
    HttpResponse::Ok().body("API is healthy ✅")
}
