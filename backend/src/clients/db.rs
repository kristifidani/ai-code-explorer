use crate::error::Result;
use serde::{Deserialize, Serialize};

const DB_COLLECTION_PROJECTS: &str = "projects";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Project {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<mongodb::bson::oid::ObjectId>,
    pub github_url: String,
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

impl ProjectRepositoryImpl {
    pub async fn insert_if_not_exists(&self, project: Project) -> Result<bool> {
        let filter = mongodb::bson::doc! { "github_url": &project.github_url };
        match self.collection.find_one(filter).await {
            Ok(Some(_)) => Ok(false), // Already exists
            Ok(None) => {
                self.collection.insert_one(project).await.map_err(|e| {
                    tracing::error!("Failed to insert project: {}", e);
                    crate::error::Error::MongoDBError(e)
                })?;
                Ok(true)
            }
            Err(e) => {
                tracing::error!("Failed to check project existence: {}", e);
                Err(crate::error::Error::MongoDBError(e))
            }
        }
    }

    pub async fn find_by_id(&self, id: mongodb::bson::oid::ObjectId) -> Result<Option<Project>> {
        let filter = mongodb::bson::doc! { "_id": id };
        self.collection.find_one(filter).await.map_err(|e| {
            tracing::error!("Failed to find project by id: {}", e);
            crate::error::Error::MongoDBError(e)
        })
    }
}
