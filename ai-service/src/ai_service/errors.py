class AIServiceError(Exception):
    """Base exception for all AI service errors."""


class EmbeddingError(AIServiceError):
    @classmethod
    def empty_input(cls) -> "EmbeddingError":
        return cls("Cannot embed empty or whitespace-only texts")


class LLMQueryError(AIServiceError):
    @classmethod
    def query_failed(cls, error) -> "LLMQueryError":
        return cls(f"Failed to query Ollama: {error}")


class DatabaseError(AIServiceError):
    @classmethod
    def add_chunks_failed(cls, error) -> "DatabaseError":
        return cls(f"Failed to add chunks: {error}")

    @classmethod
    def query_chunks_failed(cls, error) -> "DatabaseError":
        return cls(f"Failed to query chunks: {error}")


class NotFound(AIServiceError):
    @classmethod
    def env_variable(cls, name: str) -> "NotFound":
        return cls(f"Missing {name} environment variable")


class InvalidParam(AIServiceError):
    @classmethod
    def empty_embedding(cls) -> "InvalidParam":
        return cls("Query embedding is empty.")

    @classmethod
    def invalid_results_count(cls) -> "InvalidParam":
        return cls("number_of_results must be an integer between 1 and 100")

    @classmethod
    def invalid_repo_url(cls) -> "InvalidParam":
        return cls("Invalid GitHub repository URL format")

    @classmethod
    def git_clone_failed(cls, error=None) -> "InvalidParam":
        msg = "Failed to clone GitHub repository."
        if error:
            msg += f" Details: {error}"
        return cls(msg)
