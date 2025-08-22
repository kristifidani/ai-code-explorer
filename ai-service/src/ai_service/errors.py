class AIServiceError(Exception):
    """Base exception for all AI service errors."""


class ChunkinggError(AIServiceError):
    @classmethod
    def chunking_config(cls) -> "ChunkinggError":
        return cls("chunk_size must be greater than overlap")


class EmbeddingError(AIServiceError):
    @classmethod
    def empty_input(cls) -> "EmbeddingError":
        return cls("Cannot embed empty or whitespace-only texts")

    @classmethod
    def model_load_failed(cls, model_name: str, error: Exception) -> "EmbeddingError":
        return cls(f"Failed to load embedding model '{model_name}': {error}")

    @classmethod
    def missing_model(cls) -> "EmbeddingError":
        return cls("Embedding model not initialized.")


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

    @classmethod
    def no_repo_context(cls, error: Exception) -> "DatabaseError":
        return cls(f"No repository context set. Call set_repo_context() first. {error}")

    @classmethod
    def missing_db_init(cls) -> "DatabaseError":
        return cls("DB not initialized.")


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
        return cls("number_of_results must be an integer between 1 and 50")

    @classmethod
    def embeddings_count_mismatch(cls) -> "InvalidParam":
        return cls("Number of embeddings must match number of chunks")


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
