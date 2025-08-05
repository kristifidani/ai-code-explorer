use crate::{error::Error, error::Result};
use reqwest::{Client, StatusCode};
use url::Url;

#[derive(Clone)]
pub struct AiServiceClient {
    client: Client,
    base_url: String,
}

impl AiServiceClient {
    pub fn new(base_url: &str) -> Self {
        Self {
            client: Client::new(),
            base_url: base_url.into(),
        }
    }

    pub async fn ingest(&self, repo_url: &str) -> Result<()> {
        let base = Url::parse(&self.base_url).map_err(Error::ParseError)?;
        let url = base.join("ingest").map_err(Error::ParseError)?;
        let payload = serde_json::json!({ "repo_url": repo_url });
        let response = self.client.post(url).json(&payload).send().await?;

        match response.status() {
            StatusCode::OK => Ok(()),
            _ => {
                let code = response.status();
                let body = response.text().await?;
                tracing::error!(
                    "Failed to load github project: Response status: {}, Response text: {}",
                    code,
                    if body.len() > 200 {
                        &body[..200]
                    } else {
                        &body
                    }
                );
                Err(Error::UnexpectedResponse { code, body })
            }
        }
    }
}
