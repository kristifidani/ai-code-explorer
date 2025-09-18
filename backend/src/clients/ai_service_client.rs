use crate::{
    error::{Error, Result},
    types::internal::{AiServiceAnswerRequest, AiServiceAnswerResponse, AiServiceIngestRequest},
};
use reqwest::{Client, StatusCode};

#[async_trait::async_trait]
pub(crate) trait AiServiceClientImpl: Send + Sync + 'static {
    async fn ingest(&self, url: &url::Url) -> Result<()>;
    async fn answer(
        &self,
        url: Option<&url::Url>,
        question: &str,
    ) -> Result<AiServiceAnswerResponse>;
}

#[derive(Clone)]
pub struct AiServiceClient {
    client: Client,
    base_url: url::Url,
}

impl AiServiceClient {
    pub fn new(base_url: url::Url) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
}

#[async_trait::async_trait]
impl AiServiceClientImpl for AiServiceClient {
    async fn ingest(&self, url: &url::Url) -> Result<()> {
        let request_url = self.base_url.join("ingest")?;
        let payload = AiServiceIngestRequest {
            canonical_github_url: url.clone(),
        };
        let response = self.client.post(request_url).json(&payload).send().await?;

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

    async fn answer(
        &self,
        url: Option<&url::Url>,
        question: &str,
    ) -> Result<AiServiceAnswerResponse> {
        let request_url = self.base_url.join("answer")?;
        let payload = AiServiceAnswerRequest {
            canonical_github_url: url.cloned(),
            user_question: question.to_string(),
        };
        let response = self.client.post(request_url).json(&payload).send().await?;

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
