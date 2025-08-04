use crate::error::Result;
use crate::{Error, db::ProjectRepository};
use actix_web::{
    HttpResponse, Responder,
    web::{Data, Json, Path},
};
use mongodb::bson::oid::ObjectId;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct AnswerRequest {
    pub question: String,
}

pub async fn answer_question(
    repo: Data<dyn ProjectRepository>,
    path: Path<String>,
    req: Json<AnswerRequest>,
) -> Result<impl Responder> {
    let project_id = path.into_inner();
    let obj_id =
        ObjectId::parse_str(&project_id).map_err(|e| Error::InvalidProjectId(e.to_string()))?;

    let project = repo
        .find_by_id(obj_id)
        .await?
        .ok_or(Error::ProjectNotFound(obj_id.to_string()))?;

    // TODO: integrate with ai-service

    Ok(HttpResponse::Ok().body(format!(
        "Answering for project {}: {}",
        project.github_url, req.question
    )))
}
