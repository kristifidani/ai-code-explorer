use crate::clients::{
    ai_service_client::{AiServiceClient, AiServiceClientImpl},
    db::{ProjectRepository, ProjectRepositoryImpl},
};
use crate::error::Result;
use crate::types::{
    entities::ProjectEntity,
    external::{IngestRequest, IngestResponse},
    response::ApiResponse,
};
use actix_web::{
    Responder,
    http::StatusCode,
    web::{Data, Json},
};

pub async fn ingest(
    project_repo: Data<ProjectRepository>,
    ai_client: Data<AiServiceClient>,
    req: Json<IngestRequest>,
) -> Result<impl Responder> {
    // Create and validate project with canonical URL
    let project = ProjectEntity::new_validated(&req.github_url)?;
    let canonical_github_url = &project.canonical_github_url;

    // Check if project already exists
    if project_repo
        .find_by_canonical_github_url(canonical_github_url)
        .await?
        .is_some()
    {
        tracing::info!("Project already exists: {}", canonical_github_url);

        return Ok(ApiResponse::new(
            StatusCode::CONFLICT,
            Some(IngestResponse {
                canonical_github_url: canonical_github_url.clone(),
            }),
            "Project already exists and is ready to use",
        )
        .into_response());
    }

    // Ingest into the ai service
    ai_client.ingest(canonical_github_url).await?;

    // Store in DB
    project_repo.create(&project).await?;
    tracing::info!("Ingested: {}", canonical_github_url);

    Ok(ApiResponse::new(
        StatusCode::CREATED,
        Some(IngestResponse {
            canonical_github_url: canonical_github_url.clone(),
        }),
        "Project ingested successfully",
    )
    .into_response())
}
