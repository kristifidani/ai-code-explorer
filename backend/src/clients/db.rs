use crate::{error::Result, types::entities::ProjectEntity};

const DB_COLLECTION_PROJECTS: &str = "projects";

#[async_trait::async_trait]
pub trait ProjectRepositoryImpl: Send + Sync + 'static {
    async fn find_by_github_url(&self, github_url: &str) -> Result<Option<ProjectEntity>>;
    async fn create(&self, project: ProjectEntity) -> Result<ProjectEntity>;
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
    async fn find_by_github_url(&self, github_url: &str) -> Result<Option<ProjectEntity>> {
        let filter = mongodb::bson::doc! { "github_url": github_url };
        self.collection.find_one(filter).await.map_err(|e| {
            tracing::error!("Failed to find project by GitHub URL: {}", e);
            crate::error::Error::MongoDBError(e)
        })
    }

    async fn create(&self, project: ProjectEntity) -> Result<ProjectEntity> {
        self.collection.insert_one(&project).await.map_err(|e| {
            tracing::error!("Failed to insert project: {}", e);
            crate::error::Error::MongoDBError(e)
        })?;
        Ok(project)
    }
}
