use crate::{
    error::Result,
    handlers::ai::{answer::answer_question, ingest_project::ingest},
};
use actix_web::{HttpRequest, HttpResponse, Responder, web};

pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(web::resource("/health").route(web::get().to(health_check)));
    cfg.service(web::resource("/projects").route(web::post().to(ingest)));
    cfg.service(web::resource("/projects/{id}/answer").route(web::post().to(answer_question)));
}

pub async fn health_check(_: HttpRequest) -> Result<impl Responder> {
    tracing::debug!("Health check!");
    Ok(HttpResponse::Ok().body("API is healthy ✅"))
}
