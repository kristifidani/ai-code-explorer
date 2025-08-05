use crate::error::Result;
use crate::types::answer::AnswerRequest;
use crate::{
    Error,
    clients::db::{ProjectRepository, ProjectRepositoryImpl},
};
use actix_web::{
    HttpResponse, Responder,
    web::{Data, Json, Query},
};
use serde::Deserialize;

#[derive(Deserialize)]
pub struct AnswerQuery {
    pub github_url: String,
}

pub async fn answer_question(
    repo: Data<ProjectRepositoryImpl>,
    query: Query<AnswerQuery>,
    req: Json<AnswerRequest>,
) -> Result<impl Responder> {
    let project = repo
        .find_by_github_url(&query.github_url)
        .await?
        .ok_or(Error::ProjectNotFound(query.github_url.clone()))?;

    // TODO: integrate with ai-service

    Ok(HttpResponse::Ok().body(format!(
        "Answering for project {}: {}",
        project.github_url, req.question
    )))
}
