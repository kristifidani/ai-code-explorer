class AIServiceError(Exception):
    """Base exception for all AI service errors."""


class EmbeddingError(AIServiceError):
    @classmethod
    def empty_input(cls) -> "EmbeddingError":
        return cls("Cannot embed empty or whitespace-only texts")


class LLMQueryError(AIServiceError):
    @classmethod
    def query_failed(cls, error: Exception) -> "LLMQueryError":
        return cls(f"Failed to query Ollama: {error}")


class DatabaseError(AIServiceError):
    @classmethod
    def add_chunks_failed(cls, error: Exception) -> "DatabaseError":
        return cls(f"Failed to add chunks: {error}")

    @classmethod
    def query_chunks_failed(cls, error: Exception) -> "DatabaseError":
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


class GitCloneError(AIServiceError):
    @classmethod
    def failed(cls, error: Exception) -> "GitCloneError":
        return cls(f"Failed to clone GitHub repository: {error}")


class FileReadError(AIServiceError):
    @classmethod
    def file_not_found(cls, file_path: str) -> "FileReadError":
        return cls(f"File not found: {file_path}")

    @classmethod
    def permission_denied(cls, file_path: str) -> "FileReadError":
        return cls(f"Permission denied: {file_path}")

    @classmethod
    def decode_error(cls, file_path: str) -> "FileReadError":
        return cls(f"Unicode decode error in file: {file_path}")

    @classmethod
    def os_error(cls, file_path: str, error: Exception) -> "FileReadError":
        return cls(f"OS error reading file {file_path}: {error}")
