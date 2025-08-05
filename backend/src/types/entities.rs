use serde::{Deserialize, Serialize};
use url::Url;

use crate::Error;

#[derive(Serialize, Deserialize)]
pub struct Project {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<mongodb::bson::oid::ObjectId>,
    pub github_url: String,
}

impl Project {
    pub fn new(github_url: String) -> Self {
        Self {
            id: None,
            github_url,
        }
    }

    pub fn validate_github_url(&self) -> crate::error::Result<()> {
        // Parse as URL first
        let url = Url::parse(&self.github_url).map_err(Error::ParseError)?;

        // Check if it's a GitHub URL
        if url.host_str() != Some("github.com") {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL must be from github.com".to_string(),
            ));
        }

        // Check if url ends with `.git` for HTTPS
        if !self.github_url.ends_with(".git") {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL must end with .git".to_string(),
            ));
        }

        // Check path format (should be /{owner}/{repo}.git)
        let path = url.path();
        let path_parts: Vec<&str> = path
            .trim_start_matches('/')
            .trim_end_matches('/')
            .split('/')
            .collect();

        if path_parts.len() != 2 || path_parts[0].is_empty() || path_parts[1].is_empty() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "GitHub URL must be in format: https://github.com/owner/repo.git".to_string(),
            ));
        }

        // Check for valid GitHub repository name characters
        let valid_chars = |s: &str| {
            s.chars()
                .all(|c| c.is_alphanumeric() || c == '-' || c == '_' || c == '.')
        };
        let repo_name = path_parts[1].trim_end_matches(".git");
        if !valid_chars(path_parts[0]) || !valid_chars(repo_name) {
            return Err(crate::error::Error::InvalidGithubUrl("Repository owner and name can only contain alphanumeric characters, hyphens, underscores, and dots".to_string()));
        }

        Ok(())
    }
}
