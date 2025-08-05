use crate::clients::ai_service_client::{AiServiceClient, AiServiceClientImpl};
use crate::clients::db::{ProjectRepository, ProjectRepositoryImpl};
use crate::error::Result;
use crate::types::entities::Project;
use crate::types::ingestion::IngestRequest;
use actix_web::{
    HttpResponse, Responder,
    web::{Data, Json},
};

pub async fn ingest(
    repo: Data<ProjectRepositoryImpl>,
    ai_client: Data<AiServiceClientImpl>,
    req: Json<IngestRequest>,
) -> Result<impl Responder> {
    // Create and validate project before any database operations
    let project = Project::new(req.github_url.clone());
    project.validate_github_url()?;

    // Check if project already exists
    if repo.exists_by_github_url(&project.github_url).await? {
        tracing::info!("Project already exists: {}", project.github_url);
        return Ok(HttpResponse::Ok().body("Project already exists."));
    }

    // Call AI service first (validate the repo can be processed)
    match ai_client.ingest(&project.github_url).await {
        Ok(_) => {
            // Only store in DB if AI service ingestion succeeds
            let created_project = repo.create(project).await?;
            tracing::info!(
                "Successfully ingested new project: {}",
                created_project.github_url
            );
            Ok(HttpResponse::Created().body("Project ingested with success."))
        }
        Err(e) => {
            tracing::error!(
                "AI service ingestion failed for {}: {}",
                project.github_url,
                e
            );
            Err(e)
        }
    }
}
