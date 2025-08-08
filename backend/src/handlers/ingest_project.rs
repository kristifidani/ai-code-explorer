use crate::clients::{
    ai_service_client::{AiServiceClient, AiServiceClientImpl},
    db::{ProjectRepository, ProjectRepositoryImpl},
};
use crate::error::Result;
use crate::types::{entities::ProjectEntity, ingestion::IngestRequest};
use actix_web::{
    HttpResponse, Responder,
    web::{Data, Json},
};

pub async fn ingest(
    project_repo: Data<ProjectRepository>,
    ai_client: Data<AiServiceClient>,
    req: Json<IngestRequest>,
) -> Result<impl Responder> {
    // Create and validate project
    let project = ProjectEntity::new(req.github_url.clone());
    project.validate_github_url()?;

    // Check if project already exists
    if project_repo
        .find_by_github_url(&project.github_url)
        .await?
        .is_some()
    {
        tracing::info!("Project already exists: {}", project.github_url);
        return Ok(HttpResponse::Ok().body("Project already exists."));
    }

    // Ingest into the ai service
    ai_client.ingest(&project.github_url).await?;

    // Only store in DB if AI service ingestion succeeds
    let created_project = project_repo.create(project).await?;
    tracing::info!("Ingested: {}", created_project.github_url);

    Ok(HttpResponse::Created().body("Project ingested with success."))
}
