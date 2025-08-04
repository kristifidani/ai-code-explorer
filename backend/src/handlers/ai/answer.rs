use crate::error::Result;
use actix_web::{
    HttpResponse, Responder,
    web::{self, Json},
};
use serde::Deserialize;

#[derive(Deserialize)]
pub struct AnswerRequest {
    pub question: String,
}

pub async fn answer_question(
    path: web::Path<String>,
    req: Json<AnswerRequest>,
) -> Result<impl Responder> {
    let project_id = path.into_inner();
    // TODO: Forward question to ai-service with project_id
    // Placeholder response
    Ok(HttpResponse::Ok().body(format!(
        "Answering for project {}: {}",
        project_id, req.question
    )))
}
