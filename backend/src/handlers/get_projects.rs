use crate::clients::db::{ProjectRepository, ProjectRepositoryImpl};
use crate::error::Result;
use crate::types::response::ApiResponse;
use actix_web::{Responder, http::StatusCode, web::Data};

pub async fn get_projects(project_repo: Data<ProjectRepository>) -> Result<impl Responder> {
    tracing::info!("Retrieving all projects ...");
    let projects = project_repo.get_all_projects().await?;

    Ok(ApiResponse::new(
        StatusCode::OK,
        Some(projects),
        "Projects retrieved successfully",
    )
    .into_response())
}
