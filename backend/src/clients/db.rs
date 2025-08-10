use crate::{error::Result, types::entities::ProjectEntity};

const DB_COLLECTION_PROJECTS: &str = "projects";

#[async_trait::async_trait]
pub trait ProjectRepositoryImpl: Send + Sync + 'static {
    async fn find_by_github_url(&self, github_url: &str) -> Result<Option<ProjectEntity>>;
    async fn create(&self, project: &ProjectEntity) -> Result<()>;
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
}

#[cfg(test)]
mod tests {
    use mongodb::Client;

    use crate::utils::parse_env_expect;

    #[tokio::test]
    async fn test_mongo_connection() {
        // Load environment variables from .env file
        dotenvy::dotenv().ok();

        // Simple test to verify MongoDB connection works
        let mongo_uri: String = parse_env_expect("MONGO_URI");
        let client = Client::with_uri_str(&mongo_uri)
            .await
            .expect("Failed to connect to MongoDB");

        // Try to list databases to verify connection
        let result = client.list_database_names().await;
        result.unwrap();
    }
}
