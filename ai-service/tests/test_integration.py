from ai_service.embedder import embed_text
from ai_service.db import add_chunks, collection
import pytest


def test_embed_store_and_retrieve():
    sample_text = "def greet(): print('Hello!')"
    embedding = embed_text(sample_text)  # returns a 1D numpy array

    # add_chunks expects a list of texts and a 2D array of embeddings
    add_chunks([sample_text], [embedding])

    # Query for the embedding we just stored
    result = collection.query(query_embeddings=[embedding], n_results=1)
    retrieved_text = result["documents"][0][0]

    assert retrieved_text == sample_text


def test_embed_empty_text_raises_value_error():
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only text"):
        embed_text("")


def test_embed_whitespace_text_raises_value_error():
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only text"):
        embed_text("   ")
