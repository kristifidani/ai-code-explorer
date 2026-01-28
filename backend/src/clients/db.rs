use crate::{error::Result, types::entities::ProjectEntity};
use futures::StreamExt;

const DB_COLLECTION_PROJECTS: &str = "projects";

#[async_trait::async_trait]
pub trait ProjectRepositoryImpl: Send + Sync + 'static {
    async fn find_by_canonical_github_url(&self, url: &url::Url) -> Result<Option<ProjectEntity>>;
    async fn create(&self, project: &ProjectEntity) -> Result<()>;
    async fn get_all_projects(&self) -> Result<Vec<ProjectEntity>>;
}

#[derive(Clone)]
pub struct ProjectRepository {
    collection: mongodb::Collection<ProjectEntity>,
}

impl ProjectRepository {
    pub fn new(client: &mongodb::Client, db_name: &str) -> Self {
        let db = client.database(db_name);
        let collection = db.collection::<ProjectEntity>(DB_COLLECTION_PROJECTS);
        Self { collection }
    }
}

#[async_trait::async_trait]
impl ProjectRepositoryImpl for ProjectRepository {
    async fn find_by_canonical_github_url(&self, url: &url::Url) -> Result<Option<ProjectEntity>> {
        let filter = mongodb::bson::doc! { "canonical_github_url": url.as_str() };

        Ok(self.collection.find_one(filter).await.map_err(|e| {
            tracing::error!("Failed to find project by GitHub URL: {}", e);
            e
        })?)
    }

    async fn create(&self, project: &ProjectEntity) -> Result<()> {
        self.collection.insert_one(project).await.map_err(|e| {
            tracing::error!("Failed to insert project: {}", e);
            e
        })?;

        Ok(())
    }

    async fn get_all_projects(&self) -> Result<Vec<ProjectEntity>> {
        let mut cursor = self
            .collection
            .find(mongodb::bson::doc! {})
            .await
            .map_err(|e| {
                tracing::error!("Failed to retrieve projects: {}", e);
                e
            })?;

        let mut projects = Vec::new();
        while let Some(project) = cursor.next().await {
            projects.push(project?);
        }

        Ok(projects)
    }
}
