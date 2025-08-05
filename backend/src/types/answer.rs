use serde::Deserialize;

#[derive(Deserialize)]
pub struct AnswerRequest {
    pub question: String,
}
