use crate::{
    error::Result,
    handlers::{answer_question::answer_question, ingest_project::ingest},
    types::response::ApiResponse,
};
use actix_web::{HttpRequest, Responder, http::StatusCode, web};

pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(web::resource("/health").route(web::get().to(health_check)));
    cfg.service(
        web::scope("/v1")
            .service(web::resource("/ingest").route(web::post().to(ingest)))
            .service(web::resource("/answer").route(web::post().to(answer_question))),
    );
}

pub async fn health_check(_: HttpRequest) -> Result<impl Responder> {
    tracing::debug!("Health check!");
    Ok(ApiResponse::<()>::new(StatusCode::OK, None, "API is healthy ✅").into_response())
}
