use crate::error::Result;
use actix_web::{HttpResponse, Responder, web::Json};
use serde::Deserialize;

#[derive(Deserialize)]
pub struct IngestRequest {
    pub github_url: String,
}

pub async fn ingest(req: Json<IngestRequest>) -> Result<impl Responder> {
    // TODO: Connect to MongoDB, check if project exists, call ai-service if not
    // Placeholder response
    Ok(HttpResponse::Ok().body(format!("Ingesting project: {}", req.github_url)))
}
