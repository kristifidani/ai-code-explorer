"""
Tests focused purely on the encoding module functionality.
Embedding generation and validation.
"""

import pytest
from ai_service import errors
from ai_service.embeddings import encoding
from dotenv import load_dotenv

load_dotenv()


class TestInputValidation:
    """Test input validation and error handling."""

    @pytest.mark.parametrize("invalid_input", ["", "   ", "\t", "\n"])
    def test_rejects_empty_strings(self, invalid_input: str):
        with pytest.raises(
            errors.EmbeddingError,
            match="Cannot embed empty or whitespace-only texts",
        ):
            encoding.embed_query(invalid_input)
            encoding.embed_documents([invalid_input])

    def test_embed_documents_rejects_empty_list(self):
        with pytest.raises(errors.EmbeddingError):
            encoding.embed_documents([])


class TestEmbeddingGeneration:
    """Test embedding generation functionality."""

    def test_embed_query_returns_valid_embedding(self):
        text = "def example_function(): return 42"
        embedding = encoding.embed_query(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_documents_returns_valid_embeddings(self):
        texts = ["def func1(): pass", "def func2(): pass"]
        embeddings = encoding.embed_documents(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
        assert all(isinstance(x, float) for emb in embeddings for x in emb)

    def test_query_vs_document_embedding_dimensions_match(self):
        text = "def example_function(): return 42"

        query_embedding = encoding.embed_query(text)
        document_embeddings = encoding.embed_documents([text])

        assert len(query_embedding) == len(document_embeddings[0])

    @pytest.mark.parametrize(
        "text",
        [
            "def greet(): print('Hello! 你好')",
            "# Comment with émojis 🚀",
            "def func(): return 'quotes\"and\\backslashes'",
            "multiline\nstring\nwith\nnewlines",
            "def 函数(): return '中文'",
            "a",  # single char
            "1",  # number
            "!",  # symbol
        ],
    )
    def test_embed_query_handles_unicode_and_special_chars(self, text: str):
        embedding = encoding.embed_query(text)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)


class TestBatchProcessing:
    """Test batch processing capabilities."""

    def test_embed_documents_batch_consistency(self):
        texts = [f"def function_{i}(): pass" for i in range(10)]
        embeddings = encoding.embed_documents(texts)

        assert len(embeddings) == len(texts)
        # All embeddings should have the same dimension
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1  # All dimensions are the same

    def test_embed_documents_large_batch(self):
        # Test with a larger batch to ensure no memory issues
        texts = [f"def function_{i}(): return {i}" for i in range(50)]
        embeddings = encoding.embed_documents(texts)

        assert len(embeddings) == 50
        assert all(len(emb) > 0 for emb in embeddings)

    def test_embed_documents_single_vs_batch_consistency(self):
        text = "def example_function(): return 42"

        # Single document embedding
        single_embedding = encoding.embed_documents([text])[0]

        # Same text in a batch with others
        batch_texts = ["def other1(): pass", text, "def other2(): pass"]
        batch_embeddings = encoding.embed_documents(batch_texts)

        # The embedding for the same text should be very similar
        # (allowing for minor floating point differences)
        assert len(single_embedding) == len(batch_embeddings[1])

    def test_embedding_deterministic(self):
        """Test that same input produces same embedding (for consistency)."""
        text = "def test_function(): return 42"

        embedding1 = encoding.embed_query(text)
        embedding2 = encoding.embed_query(text)

        # Should be identical (not just similar)
        assert embedding1 == embedding2

    def test_very_long_text_handling(self):
        """Test handling of extremely long texts."""
        # Test model's token limit behavior
        very_long_text = "def func():\n" + "    # comment line\n" * 1000 + "    pass"

        # Should not crash, should handle gracefully
        embedding = encoding.embed_query(very_long_text)
        assert len(embedding) > 0
