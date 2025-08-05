use serde::Deserialize;

#[derive(Deserialize)]
pub struct IngestRequest {
    pub github_url: String,
}
