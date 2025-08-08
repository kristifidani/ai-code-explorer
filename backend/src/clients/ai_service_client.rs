use crate::{error::Error, error::Result};
use reqwest::{Client, StatusCode};
use url::Url;

#[async_trait::async_trait]
pub trait AiServiceClientImpl: Send + Sync + 'static {
    async fn ingest(&self, repo_url: &str) -> Result<()>;
    // async fn answer(&self, repo_url: &str, question: &str) -> Result<String>;
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
                    "Failed to ingest github project: Response status: {}, Response text: {}",
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

    // async fn answer(&self, repo_url: &str, question: &str) -> Result<String> {
    //     let base = Url::parse(&self.base_url).map_err(Error::ParseError)?;
    //     let url = base.join("answer").map_err(Error::ParseError)?;
    //     let payload = serde_json::json!({
    //         "repo_url": repo_url,
    //         "user_question": question
    //     });
    //     let response = self.client.post(url).json(&payload).send().await?;

    //     match response.status() {
    //         StatusCode::OK => {
    //             let response_body: serde_json::Value = response.json().await?;
    //             let answer =
    //                 response_body["answer"]
    //                     .as_str()
    //                     .ok_or_else(|| Error::UnexpectedResponse {
    //                         code: StatusCode::OK,
    //                         body: "Missing 'answer' field in response".to_string(),
    //                     })?;
    //             Ok(answer.to_string())
    //         }
    //         _ => {
    //             let code = response.status();
    //             let body = response.text().await?;
    //             tracing::error!(
    //                 "Failed to get answer from AI service: Response status: {}, Response text: {}",
    //                 code,
    //                 if body.len() > 200 {
    //                     &body[..200]
    //                 } else {
    //                     &body
    //                 }
    //             );
    //             Err(Error::UnexpectedResponse { code, body })
    //         }
    //     }
    // }
}
