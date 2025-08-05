use crate::clients::ai_service_client::AiServiceClient;
use crate::clients::db::{Project, ProjectRepositoryImpl};
use crate::error::Result;
use actix_web::{
    HttpResponse, Responder,
    web::{Data, Json},
};
use serde::Deserialize;

#[derive(Deserialize)]
pub struct IngestRequest {
    pub github_url: String,
}

pub async fn ingest(
    repo: Data<ProjectRepositoryImpl>,
    ai_client: Data<AiServiceClient>,
    req: Json<IngestRequest>,
) -> Result<impl Responder> {
    let project = Project {
        id: None,
        github_url: req.github_url.clone(),
    };

    if repo.insert_if_not_exists(project).await? {
        ai_client.ingest(&req.github_url).await?;
        tracing::info!("Successfully ingested new project: {}", req.github_url);
        Ok(HttpResponse::Created().body("Project ingested with success."))
    } else {
        tracing::info!("Project already exists: {}", req.github_url);
        Ok(HttpResponse::Ok().body("Project already exists."))
    }
}
