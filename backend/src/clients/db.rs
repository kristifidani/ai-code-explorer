use crate::{error::Result, types::entities::Project};

const DB_COLLECTION_PROJECTS: &str = "projects";

#[async_trait::async_trait]
pub trait ProjectRepository: Send + Sync + 'static {
    async fn find_by_github_url(&self, github_url: &str) -> Result<Option<Project>>;
    async fn create(&self, project: Project) -> Result<Project>;
    async fn exists_by_github_url(&self, github_url: &str) -> Result<bool>;
}

#[derive(Clone)]
pub struct ProjectRepositoryImpl {
    collection: mongodb::Collection<Project>,
}

impl ProjectRepositoryImpl {
    pub fn new(client: &mongodb::Client, db_name: &str) -> Self {
        let db = client.database(db_name);
        let collection = db.collection::<Project>(DB_COLLECTION_PROJECTS);
        Self { collection }
    }
}

#[async_trait::async_trait]
impl ProjectRepository for ProjectRepositoryImpl {
    async fn find_by_github_url(&self, github_url: &str) -> Result<Option<Project>> {
        let filter = mongodb::bson::doc! { "github_url": github_url };
        self.collection.find_one(filter).await.map_err(|e| {
            tracing::error!("Failed to find project by GitHub URL: {}", e);
            crate::error::Error::MongoDBError(e)
        })
    }

    async fn create(&self, project: Project) -> Result<Project> {
        self.collection.insert_one(&project).await.map_err(|e| {
            tracing::error!("Failed to insert project: {}", e);
            crate::error::Error::MongoDBError(e)
        })?;
        Ok(project)
    }

    async fn exists_by_github_url(&self, github_url: &str) -> Result<bool> {
        let filter = mongodb::bson::doc! { "github_url": github_url };
        let count = self.collection.count_documents(filter).await.map_err(|e| {
            tracing::error!("Failed to check project existence: {}", e);
            crate::error::Error::MongoDBError(e)
        })?;
        Ok(count > 0)
    }
}
