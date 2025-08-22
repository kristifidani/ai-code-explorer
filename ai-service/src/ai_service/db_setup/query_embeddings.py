import chromadb
from ai_service import errors
from ai_service.db_setup.setup import get_collection


def query_chunks(
    text_embedding: list[float],
    number_of_results: int = 4,
) -> chromadb.QueryResult:
    """
    Query ChromaDB for most similar documents.

    Args:
        text_embedding: Vector embedding of a user query.
        number_of_results: Number of results to return (1-50). Default is 4.

    Returns:
        A QueryResult object containing the results.

    Raises:
        DatabaseError: If the query fails.
        InvalidParam: If parameters are invalid.
    """
    if len(text_embedding) == 0:
        raise errors.InvalidParam.empty_embedding()
    if number_of_results < 1 or number_of_results > 50:
        raise errors.InvalidParam.invalid_results_count()

    collection = get_collection()
    try:
        return collection.query(
            query_embeddings=[text_embedding],
            n_results=number_of_results,
        )
    except Exception as e:
        raise errors.DatabaseError.query_chunks_failed(e) from e
