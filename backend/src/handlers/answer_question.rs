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
    // Validate the request (trim whitespace and check for empty question)
    let validated_req = AnswerRequest::new(req.canonical_github_url.clone(), req.question.clone())?;

    // Check if the project exists in our database
    let Some(stored_project) = project_repo
        .find_by_github_url(&validated_req.canonical_github_url)
        .await?
    else {
        tracing::warn!(
            "Project not found in database: {}",
            validated_req.canonical_github_url
        );
        return Ok(ApiResponse::<()>::new(
            StatusCode::NOT_FOUND,
            None,
            "Project not found. Please ingest a project first.",
        )
        .into_response());
    };

    let stored_project_url = stored_project.canonical_github_url.clone();
    let resp = ai_client
        .answer(&stored_project_url, &validated_req.question)
        .await?;

    tracing::info!("Question answered for project: {}", stored_project_url);

    Ok(ApiResponse::new(
        StatusCode::OK,
        Some(AnswerResponse {
            answer: resp.answer,
        }),
        "Question answered successfully",
    )
    .into_response())
}
