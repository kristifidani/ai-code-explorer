class AIServiceError(Exception):
    """Base exception for all AI service errors."""

    pass


class EmbeddingError(AIServiceError):
    """Base exception for embedding errors."""

    @classmethod
    def empty_input(cls):
        return cls("Cannot embed empty or whitespace-only texts")


class LLMQueryError(AIServiceError):
    """Raised when querying the LLM fails."""

    pass


class DatabaseError(AIServiceError):
    """Raised when database operations fail."""

    pass


class NotFound(AIServiceError):
    """Raised when something is not found."""

    @classmethod
    def env_variable(cls, name: str):
        return cls(f"Missing {name} environment variable")


class InvalidParam(AIServiceError):
    """Raised when something is invalid."""

    @classmethod
    def empty_embedding(cls):
        return cls("Query embedding is empty.")

    @classmethod
    def invalid_results_count(cls):
        return cls("number_of_results must be an integer between 1 and 100")
