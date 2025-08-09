use serde::{Deserialize, Serialize};
use url::Url;

#[derive(Serialize, Deserialize)]
#[cfg_attr(test, derive(Debug))]
pub struct ProjectEntity {
    pub github_url: String,
}

impl ProjectEntity {
    /// Creates a new ProjectEntity with a canonicalized and validated GitHub URL
    pub fn new_validated(github_url: &str) -> crate::error::Result<Self> {
        let canonical_url = Self::canonicalize_and_validate(github_url)?;
        Ok(Self {
            github_url: canonical_url,
        })
    }

    /// Canonicalizes and validates a GitHub URL in one step
    fn canonicalize_and_validate(github_url: &str) -> crate::error::Result<String> {
        // Parse the URL
        let url = Url::parse(github_url)?;

        // Validate it's a GitHub URL with HTTPS
        if url.scheme() != "https" {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL scheme must be https".to_string(),
            ));
        }

        // Check if it's a GitHub URL
        if url.host_str() != Some("github.com") {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL must be from github.com".to_string(),
            ));
        }

        // Extract and normalize the path
        let path = url.path().trim_start_matches('/').trim_end_matches('/');
        let path_parts: Vec<&str> = path.split('/').collect();

        if path_parts.len() != 2 || path_parts[0].is_empty() || path_parts[1].is_empty() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "GitHub URL must be in format: https://github.com/owner/repo".to_string(),
            ));
        }

        // Validate characters in owner and repo names
        let valid_chars = |s: &str| {
            s.chars()
                .all(|c| c.is_alphanumeric() || c == '-' || c == '_' || c == '.')
        };
        let repo_name = path_parts[1].trim_end_matches(".git");
        if !valid_chars(path_parts[0]) || !valid_chars(repo_name) {
            return Err(crate::error::Error::InvalidGithubUrl("Repository owner and name can only contain alphanumeric characters, hyphens, underscores, and dots".to_string()));
        }

        // Canonicalize: lowercase and ensure .git suffix
        let owner = path_parts[0].to_lowercase();
        let repo = repo_name.to_lowercase();

        Ok(format!("https://github.com/{}/{}.git", owner, repo))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    #[rstest]
    #[case("https://github.com/owner/repo", "https://github.com/owner/repo.git")] // Basic case
    #[case(
        "https://github.com/owner/repo.git",
        "https://github.com/owner/repo.git"
    )] // Already has .git
    #[case("https://github.com/OWNER/REPO", "https://github.com/owner/repo.git")] // Uppercase
    #[case(
        "https://github.com/MyOwner/MyRepo.git",
        "https://github.com/myowner/myrepo.git"
    )] // Mixed case
    #[case("https://github.com/owner/repo/", "https://github.com/owner/repo.git")] // Trailing slash
    #[case(
        "https://github.com/test-user/my_repo.git",
        "https://github.com/test-user/my_repo.git"
    )] // Valid special chars
    fn test_project_entity_canonicalization_success(#[case] input: &str, #[case] expected: &str) {
        let project = ProjectEntity::new_validated(input).unwrap();
        assert_eq!(project.github_url, expected);
    }

    #[rstest]
    #[case("http://github.com/owner/repo")] // HTTP instead of HTTPS
    #[case("https://gitlab.com/owner/repo")] // Not GitHub
    #[case("https://github.com/owner")] // Missing repo
    #[case("https://github.com//repo")] // Empty owner
    #[case("https://github.com/owner/")] // Empty repo
    #[case("https://github.com/owner/repo/extra")] // Too many path segments
    #[case("https://github.com/own er/repo")] // Invalid character (space)
    #[case("https://github.com/owner/re@po")] // Invalid character (@)
    fn test_project_entity_canonicalization_failure(#[case] input: &str) {
        use crate::Error;

        let result = ProjectEntity::new_validated(input);
        assert!(matches!(result.unwrap_err(), Error::InvalidGithubUrl(_)));
    }
}
