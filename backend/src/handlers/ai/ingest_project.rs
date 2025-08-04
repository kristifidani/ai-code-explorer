use crate::db::{Project, ProjectRepository};
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
    repo: Data<dyn ProjectRepository>,
    req: Json<IngestRequest>,
) -> Result<impl Responder> {
    let project = Project {
        id: None,
        github_url: req.github_url.clone(),
    };

    match repo.insert_if_not_exists(project).await? {
        true => {
            // TODO: Call ai-service ingestion here

            Ok(HttpResponse::Created().body("Project ingested and stored."))
        }
        false => Ok(HttpResponse::Ok().body("Project already exists.")),
    }
}
