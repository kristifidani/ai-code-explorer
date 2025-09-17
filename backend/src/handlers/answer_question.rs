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
    let req = req.into_inner();
    let validated_req = AnswerRequest::new(req.canonical_github_url, req.question)?;

    let project_url = if let Some(ref canonical_url) = validated_req.canonical_github_url {
        // check is the project exists in db
        match project_repo
            .find_by_canonical_github_url(canonical_url)
            .await?
        {
            Some(stored_project) => Some(stored_project.canonical_github_url),
            None => {
                tracing::warn!("Project not found in database: {}", canonical_url);
                return Ok(ApiResponse::<()>::new(
                    StatusCode::NOT_FOUND,
                    None,
                    "Project not found. Please ingest a project first.",
                )
                .into_response());
            }
        }
    } else {
        None
    };

    let resp = ai_client
        .answer(project_url.as_ref(), &validated_req.question)
        .await?;

    if let Some(url) = &project_url {
        tracing::info!("Question answered for project: {}", url);
    } else {
        tracing::info!("General question answered: {}", validated_req.question);
    }

    Ok(ApiResponse::new(
        StatusCode::OK,
        Some(AnswerResponse {
            answer: resp.answer,
        }),
        "Question answered successfully",
    )
    .into_response())
}
