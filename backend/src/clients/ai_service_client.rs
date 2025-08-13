use crate::{
    error::{Error, Result},
    types::internal::{AiServiceAnswerRequest, AiServiceAnswerResponse, AiServiceIngestRequest},
};
use reqwest::{Client, StatusCode};
use url::Url;

#[async_trait::async_trait]
pub(crate) trait AiServiceClientImpl: Send + Sync + 'static {
    async fn ingest(&self, repo_url: &str) -> Result<()>;
    async fn answer(&self, repo_url: &str, question: &str) -> Result<AiServiceAnswerResponse>;
}

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
}

#[async_trait::async_trait]
impl AiServiceClientImpl for AiServiceClient {
    async fn ingest(&self, repo_url: &str) -> Result<()> {
        let base = Url::parse(&self.base_url)?;
        let url = base.join("ingest")?;
        let payload = AiServiceIngestRequest {
            repo_url: repo_url.to_string(),
        };
        let response = self.client.post(url).json(&payload).send().await?;

        match response.status() {
            StatusCode::CREATED => Ok(()),
            _ => {
                let code = response.status();
                let body = response.text().await?;
                tracing::error!(
                    "Failed to ingest github project: Response status: {}, Response text: {}",
                    code,
                    body
                );
                Err(Error::UnexpectedResponse { code, body })
            }
        }
    }

    async fn answer(&self, repo_url: &str, question: &str) -> Result<AiServiceAnswerResponse> {
        let base = Url::parse(&self.base_url)?;
        let url = base.join("answer")?;
        let payload = AiServiceAnswerRequest {
            repo_url: repo_url.to_string(),
            user_question: question.to_string(),
        };
        let response = self.client.post(url).json(&payload).send().await?;

        match response.status() {
            StatusCode::OK => {
                let response_data: AiServiceAnswerResponse = response.json().await?;
                Ok(response_data)
            }
            _ => {
                let code = response.status();
                let body = response.text().await?;
                tracing::error!(
                    "Failed to get answer: Response status: {}, Response text: {}",
                    code,
                    body
                );
                Err(Error::UnexpectedResponse { code, body })
            }
        }
    }
}
