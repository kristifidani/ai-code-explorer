use crate::clients::{
    ai_service_client::{AiServiceClient, AiServiceClientImpl},
    db::{ProjectRepository, ProjectRepositoryImpl},
};
use crate::error::Result;
use crate::types::{
    external::{AnswerRequest, AnswerResponse},
    response::ApiResponse,
};
use actix_web::{
    Responder,
    http::StatusCode,
    web::{Data, Json},
};

pub async fn answer_question(
    project_repo: Data<ProjectRepository>,
    ai_client: Data<AiServiceClient>,
    req: Json<AnswerRequest>,
) -> Result<impl Responder> {
    // Check if the project exists in our database
    let stored_project = project_repo.find_by_github_url(&req.repo_url).await?;

    if stored_project.is_none() {
        tracing::warn!("Project not found in database: {}", req.repo_url);
        return Ok(ApiResponse::<()>::new(
            StatusCode::NOT_FOUND,
            None,
            "Project not found. Please ingest the project first using the /ingest endpoint.",
        )
        .into_response());
    }

    // Call the AI service to get the answer
    let resp = ai_client.answer(&req.repo_url, &req.question).await?;

    tracing::info!("Question answered for project: {}", req.repo_url);

    Ok(ApiResponse::new(
        StatusCode::OK,
        Some(AnswerResponse {
            answer: resp.answer,
            project_url: req.repo_url.clone(),
        }),
        "Question answered successfully",
    )
    .into_response())
}
