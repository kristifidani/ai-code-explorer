/// Represents a project entity with a validated GitHub repository URL.
///
/// This struct ensures that only valid GitHub repository URLs are stored,
/// following GitHub's official naming conventions and URL structure requirements.
/// The URL is canonicalized to the standard format: https://github.com/owner/repo.git
///
/// # GitHub Repository URL Requirements
///
/// ## URL Structure
/// - Must use HTTPS protocol
/// - Must be from github.com domain
/// - Must follow the pattern: https://github.com/owner/repo[.git]
/// - Cannot contain fragments (#) or query parameters (?)
/// - Path must have exactly 2 segments (owner and repository)
///
/// ## Owner/Organization Name Rules
/// **Source**: [GitHub Docs - Username considerations for external authentication](https://docs.github.com/en/admin/identity-and-access-management/iam-configuration-reference/username-considerations-for-external-authentication)
///
/// - Can only contain alphanumeric characters and hyphens (`-`)
/// - Cannot start or end with a hyphen
/// - Cannot contain consecutive hyphens (`--`)
/// - Maximum length: 39 characters
/// - Case-insensitive (normalized to lowercase)
///
/// ## Repository Name Rules
/// **Source**: [GitHub Docs - Repository naming conventions](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)
///
/// - Can contain alphanumeric characters, hyphens (`-`), underscores (`_`), and dots (`.`)
/// - Cannot start with a dot (`.`), hyphen (`-`), or underscore (`_`)
/// - Cannot end with a dot (`.`), hyphen (`-`), or underscore (`_`)
/// - Maximum length: 100 characters
/// - Case-insensitive (normalized to lowercase)
///
/// ## Git Cloning Compatibility
/// Since these URLs are used for git cloning operations in the AI service:
/// - The canonical format always includes the `.git` suffix
/// - URLs are normalized to lowercase for consistency
/// - All validation ensures the URL can be successfully cloned via `git clone`
///
///
use serde::{Deserialize, Serialize};
use url::Url;

#[derive(Serialize, Deserialize)]
#[cfg_attr(test, derive(Debug))]
pub struct ProjectEntity {
    pub github_url: String,
}

impl ProjectEntity {
    pub fn new_validated(github_url: &str) -> crate::error::Result<Self> {
        let canonical_url = Self::canonicalize_and_validate(github_url)?;
        Ok(Self {
            github_url: canonical_url,
        })
    }

    /// Canonicalizes and validates a GitHub URL according to GitHub's official rules.
    fn canonicalize_and_validate(github_url: &str) -> crate::error::Result<String> {
        // Check for empty string first
        if github_url.trim().is_empty() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL cannot be empty".to_string(),
            ));
        }

        // Parse the URL
        let url = Url::parse(github_url).map_err(|e| {
            crate::error::Error::InvalidGithubUrl(format!("Invalid URL format: {:?}", e))
        })?;

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

        // Check for fragments or queries
        if url.fragment().is_some() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL cannot contain fragments (#)".to_string(),
            ));
        }

        if url.query().is_some() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "URL cannot contain query parameters (?)".to_string(),
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

        let owner = path_parts[0];
        let repo_raw = path_parts[1];
        let repo_name = repo_raw.trim_end_matches(".git");

        // Validate owner name (GitHub username/org rules)
        Self::validate_owner_name(owner)?;

        // Validate repository name (GitHub repo rules)
        Self::validate_repo_name(repo_name)?;

        // Canonicalize: lowercase and ensure .git suffix
        let canonical_owner = owner.to_lowercase();
        let canonical_repo = repo_name.to_lowercase();

        Ok(format!(
            "https://github.com/{}/{}.git",
            canonical_owner, canonical_repo
        ))
    }

    fn validate_owner_name(owner: &str) -> crate::error::Result<()> {
        if owner.is_empty() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Owner name cannot be empty".to_string(),
            ));
        }

        if owner.len() > 39 {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Owner name cannot exceed 39 characters".to_string(),
            ));
        }

        if owner.starts_with('-')
            || owner.starts_with('.')
            || owner.starts_with('_')
            || owner.ends_with('-')
        {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Owner name cannot begin with dot, underscore, or hyphen, or end with a hyphen"
                    .to_string(),
            ));
        }

        // Check for invalid characters and consecutive hyphens
        let mut prev_char = '\0';
        for c in owner.chars() {
            if !c.is_alphanumeric() && c != '-' {
                return Err(crate::error::Error::InvalidGithubUrl(
                    "Owner name can only contain alphanumeric characters and hyphens".to_string(),
                ));
            }
            if c == '-' && prev_char == '-' {
                return Err(crate::error::Error::InvalidGithubUrl(
                    "Owner name cannot have consecutive hyphens".to_string(),
                ));
            }
            prev_char = c;
        }

        Ok(())
    }

    fn validate_repo_name(repo: &str) -> crate::error::Result<()> {
        if repo.is_empty() {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Repository name cannot be empty".to_string(),
            ));
        }

        if repo.len() > 100 {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Repository name cannot exceed 100 characters".to_string(),
            ));
        }

        if repo.starts_with('.') || repo.starts_with('-') || repo.starts_with('_') {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Repository name cannot start with a dot, hyphen, or underscore".to_string(),
            ));
        }

        if repo.ends_with('.') || repo.ends_with('-') || repo.ends_with('_') {
            return Err(crate::error::Error::InvalidGithubUrl(
                "Repository name cannot end with a dot, hyphen, or underscore".to_string(),
            ));
        }

        // Check for invalid characters
        for c in repo.chars() {
            if !c.is_alphanumeric() && c != '-' && c != '_' && c != '.' {
                return Err(crate::error::Error::InvalidGithubUrl(
                    "Repository name can only contain alphanumeric characters, hyphens, underscores, and dots".to_string(),
                ));
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    /// Tests for valid GitHub URLs that should be successfully canonicalized
    #[rstest]
    // Basic URL formats
    #[case::basic_url("https://github.com/owner/repo", "https://github.com/owner/repo.git")]
    #[case::already_has_git_suffix(
        "https://github.com/owner/repo.git",
        "https://github.com/owner/repo.git"
    )]
    #[case::trailing_slash_removal(
        "https://github.com/owner/repo/",
        "https://github.com/owner/repo.git"
    )]
    // Case normalization
    #[case::uppercase_conversion(
        "https://github.com/OWNER/REPO",
        "https://github.com/owner/repo.git"
    )]
    #[case::mixed_case_conversion(
        "https://github.com/MyOwner/MyRepo.git",
        "https://github.com/myowner/myrepo.git"
    )]
    // Owner name variations (valid according to GitHub username rules)
    #[case::owner_with_hyphens(
        "https://github.com/my-org/repo",
        "https://github.com/my-org/repo.git"
    )]
    #[case::owner_with_numbers(
        "https://github.com/user123/repo",
        "https://github.com/user123/repo.git"
    )]
    #[case::single_char_owner("https://github.com/a/repo", "https://github.com/a/repo.git")]
    #[case::max_length_owner(
        "https://github.com/thisownerisexactlythirtyninecharacters/repo",
        "https://github.com/thisownerisexactlythirtyninecharacters/repo.git"
    )]
    // Repository name variations (valid according to GitHub repo rules)
    #[case::repo_with_hyphens(
        "https://github.com/owner/my-repo",
        "https://github.com/owner/my-repo.git"
    )]
    #[case::repo_with_underscores(
        "https://github.com/owner/my_repo",
        "https://github.com/owner/my_repo.git"
    )]
    #[case::repo_with_dots(
        "https://github.com/owner/repo.name",
        "https://github.com/owner/repo.name.git"
    )]
    #[case::repo_with_numbers(
        "https://github.com/owner/repo123",
        "https://github.com/owner/repo123.git"
    )]
    #[case::single_char_repo("https://github.com/owner/a", "https://github.com/owner/a.git")]
    #[case::complex_repo_name(
        "https://github.com/owner/my-repo_name.example",
        "https://github.com/owner/my-repo_name.example.git"
    )]
    // Mixed valid characters
    #[case::all_valid_chars(
        "https://github.com/test-user123/my_repo-name.example",
        "https://github.com/test-user123/my_repo-name.example.git"
    )]
    fn test_project_entity_canonicalization_success(#[case] input: &str, #[case] expected: &str) {
        let project = ProjectEntity::new_validated(input).unwrap();
        assert_eq!(project.github_url, expected);
    }

    /// Tests for invalid GitHub URLs that should be rejected
    #[rstest]
    // Protocol and domain validation
    #[case::http_instead_of_https("http://github.com/owner/repo")]
    #[case::not_github_domain("https://gitlab.com/owner/repo")]
    #[case::missing_protocol("github.com/owner/repo")]
    #[case::wrong_protocol("ftp://github.com/owner/repo")]
    // URL structure validation
    #[case::empty_string("")]
    #[case::not_a_url("not-a-url")]
    #[case::no_path("https://github.com")]
    #[case::no_owner_repo("https://github.com/")]
    #[case::empty_owner("https://github.com//repo")]
    #[case::empty_repo("https://github.com/owner/")]
    #[case::too_many_path_segments("https://github.com/owner/repo/extra")]
    #[case::tree_path("https://github.com/owner/repo/tree/main")]
    // Fragment and query validation
    #[case::url_with_fragment("https://github.com/owner/repo#fragment")]
    #[case::url_with_query("https://github.com/owner/repo?query=param")]
    #[case::url_with_both_fragment_and_query("https://github.com/owner/repo?param=value#section")]
    // Owner name validation
    #[case::owner_starts_with_hyphen("https://github.com/-invalid/repo")]
    #[case::owner_ends_with_hyphen("https://github.com/invalid-/repo")]
    #[case::owner_consecutive_hyphens("https://github.com/my--org/repo")]
    #[case::owner_starts_with_dot("https://github.com/.hidden/repo")]
    #[case::owner_starts_with_underscore("https://github.com/_private/repo")]
    #[case::owner_with_space("https://github.com/my owner/repo")]
    #[case::owner_with_special_chars("https://github.com/user@domain/repo")]
    #[case::owner_too_long(
        "https://github.com/thisownernameiswaytoolongandexceedsthemaximumlengthof39characters/repo"
    )]
    // Repository name validation
    #[case::repo_starts_with_dot("https://github.com/owner/.hidden")]
    #[case::repo_starts_with_hyphen("https://github.com/owner/-invalid")]
    #[case::repo_starts_with_underscore("https://github.com/owner/_private")]
    #[case::repo_ends_with_dot("https://github.com/owner/invalid.")]
    #[case::repo_ends_with_hyphen("https://github.com/owner/invalid-")]
    #[case::repo_ends_with_underscore("https://github.com/owner/invalid_")]
    #[case::repo_with_special_chars("https://github.com/owner/repo@name")]
    #[case::repo_with_space("https://github.com/owner/repo name")]
    // Encoding and character validation
    #[case::url_encoded_space("https://github.com/owner/repo%20name")]
    #[case::path_traversal("https://github.com/owner/../repo")]
    #[case::unencoded_spaces("https://github.com/owner/repo with spaces")]
    // Mixed invalid scenarios
    #[case::multiple_issues("https://github.com/.invalid/repo-?param=value")]
    fn test_project_entity_canonicalization_failure(#[case] input: &str) {
        let result = ProjectEntity::new_validated(input);
        assert!(matches!(
            result.unwrap_err(),
            crate::Error::InvalidGithubUrl(_)
        ));
    }

    /// Tests for edge cases and boundary conditions
    #[rstest]
    #[case::max_repo_length(
        "https://github.com/owner/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )]
    #[case::repo_too_long(
        "https://github.com/owner/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )]
    fn test_project_entity_boundary_conditions(#[case] input: &str) {
        let result = ProjectEntity::new_validated(input);

        // Extract repo name length from URL
        let repo_part = input.split('/').next_back().unwrap();

        if repo_part.len() == 100 {
            assert!(result.is_ok(), "100-character repo name should be valid");
        } else if repo_part.len() == 101 {
            assert!(
                matches!(result.unwrap_err(), crate::Error::InvalidGithubUrl(_)),
                "101-character repo name should be invalid"
            );
        } else {
            panic!(
                "Test setup error: unexpected repo name length {}",
                repo_part.len()
            );
        }
    }
}
