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
    let github_url: &str = &project.github_url;

    // Check if project already exists
    if project_repo.find_by_github_url(github_url).await?.is_some() {
        tracing::info!("Project already exists: {}", github_url);

        return Ok(ApiResponse::new(
            StatusCode::OK,
            Some(IngestResponse {
                canonical_url: github_url.to_string(),
            }),
            "Project already exists and is ready to use",
        )
        .into_response());
    }

    // Ingest into the ai service
    ai_client.ingest(github_url).await?;

    // Store in DB
    project_repo.create(&project).await?;
    tracing::info!("Ingested: {}", github_url);

    Ok(ApiResponse::new(
        StatusCode::CREATED,
        Some(IngestResponse {
            canonical_url: github_url.to_string(),
        }),
        "Project ingested successfully",
    )
    .into_response())
}
