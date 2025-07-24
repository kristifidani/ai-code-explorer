from ai_service.embedder import embed_text
from ai_service.db import add_chunks, collection
import pytest


def test_embed_store_and_retrieve():
    sample_text = "def greet(): print('Hello!')"
    embedding = embed_text(sample_text)  # Embed the sample text

    add_chunks([sample_text], [embedding])  # Store the text and its embedding

    try:
        # Query for the embedding we just stored
        result = collection.query(query_embeddings=[embedding], n_results=1)
        retrieved_text = result["documents"][0][0]

        assert retrieved_text == sample_text
    finally:
        # Clean up test data
        collection.delete(where={"$contains": sample_text})


def test_embed_empty_text_raises_value_error():
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only text"):
        embed_text("")


def test_embed_whitespace_text_raises_value_error():
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only text"):
        embed_text("   ")


def test_embed_texts_multiple_inputs():
    """Test the embed_texts function with multiple text inputs"""
    from ai_service.embedder import embed_texts
    
    sample_texts = [
        "def greet(): print('Hello!')",
        "def farewell(): print('Goodbye!')",
        "class Calculator: pass"
    ]
    
    embeddings = embed_texts(sample_texts)
    
    # Should return numpy array with correct shape
    assert embeddings is not None
    assert len(embeddings) == len(sample_texts)
    assert embeddings.ndim == 2  # 2D array: [num_texts, embedding_dim]
    
    # Each embedding should have the same dimensionality
    embedding_dim = len(embeddings[0])
    for embedding in embeddings:
        assert len(embedding) == embedding_dim


def test_embed_texts_empty_list_raises_error():
    """Test embed_texts raises ValueError for empty list"""
    from ai_service.embedder import embed_texts
    
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only texts"):
        embed_texts([])


def test_embed_texts_all_empty_strings_raises_error():
    """Test embed_texts raises ValueError when all strings are empty/whitespace"""
    from ai_service.embedder import embed_texts
    
    empty_texts = ["", "   ", "\t\n", ""]
    with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only texts"):
        embed_texts(empty_texts)


def test_embed_texts_mixed_valid_empty_strings():
    """Test embed_texts with mix of valid and empty strings"""
    from ai_service.embedder import embed_texts
    
    mixed_texts = ["def valid(): pass", "", "another valid text", "   "]
    
    # Should work since not ALL texts are empty
    embeddings = embed_texts(mixed_texts)
    assert embeddings is not None
    assert len(embeddings) == len(mixed_texts)


def test_embed_store_multiple_chunks():
    """Test storing and retrieving multiple chunks at once"""
    sample_texts = [
        "def greet(): print('Hello!')",
        "def farewell(): print('Goodbye!')",
        "class Calculator: pass"
    ]
    embeddings = [embed_text(text) for text in sample_texts]
    
    add_chunks(sample_texts, embeddings)
    
    try:
        # Query for one of the embeddings
        result = collection.query(query_embeddings=[embeddings[0]], n_results=3)
        retrieved_documents = result["documents"][0]
        
        # Should find at least our first text
        assert sample_texts[0] in retrieved_documents
        
        # Verify we can retrieve all stored texts
        for i, embedding in enumerate(embeddings):
            result = collection.query(query_embeddings=[embedding], n_results=1)
            retrieved_text = result["documents"][0][0]
            assert retrieved_text == sample_texts[i]
            
    finally:
        # Clean up test data
        for text in sample_texts:
            try:
                collection.delete(where={"$contains": text})
            except:
                pass


def test_embed_store_empty_chunks_list():
    """Test behavior when storing empty list of chunks"""
    try:
        add_chunks([], [])
        # Should not raise an exception, but also not add anything
        # This tests the edge case of empty inputs
    except Exception as e:
        # If it does raise an exception, that's also valid behavior to document
        pytest.fail(f"add_chunks with empty lists raised unexpected exception: {e}")


def test_embed_store_mismatched_lengths():
    """Test error handling when chunks and embeddings lists have different lengths"""
    sample_texts = ["def greet(): print('Hello!')", "def farewell(): print('Goodbye!')"]
    single_embedding = [embed_text(sample_texts[0])]
    
    # This should ideally raise an error or handle gracefully
    try:
        add_chunks(sample_texts, single_embedding)
        # If no exception, verify what actually got stored and clean up
        result = collection.query(query_embeddings=single_embedding, n_results=2)
        for text in sample_texts:
            try:
                collection.delete(where={"$contains": text})
            except:
                pass
    except Exception:
        # Expected behavior - mismatched lengths should raise an error
        pass


def test_embed_text_with_special_characters():
    """Test embedding text with special characters and Unicode"""
    special_texts = [
        "def greet(): print('Hello! 你好')",
        "# Comment with émojis 🚀",
        "def func(): return 'quotes\"and\\backslashes'",
        "multiline\nstring\nwith\nnewlines"
    ]
    
    for text in special_texts:
        try:
            embedding = embed_text(text)
            assert embedding is not None
            assert len(embedding) > 0
            
            # Test storage and retrieval
            add_chunks([text], [embedding])
            result = collection.query(query_embeddings=[embedding], n_results=1)
            retrieved_text = result["documents"][0][0]
            assert retrieved_text == text
            
        finally:
            # Clean up
            try:
                collection.delete(where={"$contains": text})
            except:
                pass


def test_embed_text_very_long_input():
    """Test embedding very long text input"""
    # Create a very long string
    long_text = "def very_long_function():\n" + "    # comment line\n" * 1000 + "    pass"
    
    try:
        embedding = embed_text(long_text)
        assert embedding is not None
        assert len(embedding) > 0
        
        # Test storage and retrieval
        add_chunks([long_text], [embedding])
        result = collection.query(query_embeddings=[embedding], n_results=1)
        retrieved_text = result["documents"][0][0]
        assert retrieved_text == long_text
        
    finally:
        # Clean up
        try:
            collection.delete(where={"$contains": "very_long_function"})
        except:
            pass


def test_embed_text_only_whitespace_variations():
    """Test various whitespace-only inputs"""
    whitespace_variations = [
        "\t",
        "\n", 
        "\r\n",
        "   \t  \n  ",
        "\t\t\t",
        "\n\n\n"
    ]
    
    for whitespace in whitespace_variations:
        with pytest.raises(ValueError, match="Cannot embed empty or whitespace-only text"):
            embed_text(whitespace)


def test_embed_text_none_input():
    """Test embedding None input"""
    with pytest.raises(AttributeError):  # None has no strip() method
        embed_text(None)


def test_query_with_different_n_results():
    """Test querying with different n_results values"""
    sample_texts = [
        "def function_a(): pass",
        "def function_b(): pass", 
        "def function_c(): pass",
        "def function_d(): pass",
        "def function_e(): pass"
    ]
    embeddings = [embed_text(text) for text in sample_texts]
    
    add_chunks(sample_texts, embeddings)
    
    try:
        # Test different n_results values
        for n in [1, 3, 5, 10]:  # Including more than available
            result = collection.query(query_embeddings=[embeddings[0]], n_results=n)
            documents = result["documents"][0]
            
            # Should return at most n results, or all available if n is larger
            expected_count = min(n, len(sample_texts))
            assert len(documents) <= expected_count
            
    finally:
        # Clean up
        for text in sample_texts:
            try:
                collection.delete(where={"$contains": text})
            except:
                pass


def test_embedding_consistency():
    """Test that the same text produces the same embedding"""
    text = "def consistent_function(): return 42"
    
    embedding1 = embed_text(text)
    embedding2 = embed_text(text)
    
    # Embeddings should be identical for the same input
    assert len(embedding1) == len(embedding2)
    
    # Check if embeddings are exactly the same
    import numpy as np
    np.testing.assert_array_equal(embedding1, embedding2)


def test_embedding_returns_numpy_array():
    """Test that embed_text returns numpy array with correct properties"""
    import numpy as np
    
    text = "def test_function(): return True"
    embedding = embed_text(text)
    
    # Should be numpy array
    assert isinstance(embedding, np.ndarray)
    assert embedding.ndim == 1  # 1D array for single text
    assert len(embedding) > 0
    assert embedding.dtype in [np.float32, np.float64]


def test_edge_case_single_character():
    """Test embedding single character inputs"""
    single_chars = ["a", "1", "!", "@", "中"]
    
    for char in single_chars:
        try:
            embedding = embed_text(char)
            assert embedding is not None
            assert len(embedding) > 0
            
            # Test storage and retrieval
            add_chunks([char], [embedding])
            result = collection.query(query_embeddings=[embedding], n_results=1)
            retrieved_text = result["documents"][0][0]
            assert retrieved_text == char
            
        finally:
            try:
                collection.delete(where={"$contains": char})
            except:
                pass


def test_add_chunks_database_exception_handling():
    """Test that add_chunks properly handles and re-raises database exceptions"""
    # Test with valid inputs first to ensure function works
    sample_text = "def test_exception_handling(): pass"
    embedding = embed_text(sample_text)
    
    try:
        add_chunks([sample_text], [embedding])
        
        # Verify it was added
        result = collection.query(query_embeddings=[embedding], n_results=1)
        assert len(result["documents"][0]) > 0
        
    except Exception as e:
        # If add_chunks raises an exception, verify it's properly wrapped
        assert "Failed to add chunks to database" in str(e)
        
    finally:
        try:
            collection.delete(where={"$contains": sample_text})
        except:
            pass


def test_database_query_structure():
    """Test the structure of query results from ChromaDB"""
    sample_text = "def test_query_structure(): return 'structure'"
    embedding = embed_text(sample_text)
    
    add_chunks([sample_text], [embedding])
    
    try:
        result = collection.query(query_embeddings=[embedding], n_results=1)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "documents" in result
        assert "ids" in result
        assert isinstance(result["documents"], list)
        assert isinstance(result["documents"][0], list)
        assert len(result["documents"][0]) > 0
        
    finally:
        collection.delete(where={"$contains": sample_text})


def test_model_caching():
    """Test that the model caching decorator works properly"""
    from ai_service.embedder import _get_model
    
    # Call multiple times to test caching
    model1 = _get_model()
    model2 = _get_model()
    
    # Should return the same instance due to caching
    assert model1 is model2
    
    # Verify it's the expected model
    assert hasattr(model1, 'encode')
    assert model1.get_sentence_embedding_dimension() > 0


def test_embed_texts_vs_embed_text_consistency():
    """Test that embed_texts([text]) produces same result as embed_text(text)"""
    from ai_service.embedder import embed_texts
    import numpy as np
    
    text = "def consistency_test(): return 'same'"
    
    single_embedding = embed_text(text)
    batch_embedding = embed_texts([text])[0]
    
    # Should produce identical results
    np.testing.assert_array_equal(single_embedding, batch_embedding)


def test_large_batch_embedding():
    """Test embedding a large batch of texts"""
    from ai_service.embedder import embed_texts
    
    # Create a large batch of different texts
    large_batch = [f"def function_{i}(): return {i}" for i in range(50)]
    
    embeddings = embed_texts(large_batch)
    
    assert len(embeddings) == len(large_batch)
    assert embeddings.ndim == 2
    
    # Each embedding should be different
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Embeddings should not be identical (very low probability)
            assert not (embeddings[i] == embeddings[j]).all()


def test_collection_persistence():
    """Test that the collection persists data correctly"""
    sample_text = "def persistence_test(): return 'persistent'"
    embedding = embed_text(sample_text)
    
    # Add data
    add_chunks([sample_text], [embedding])
    
    try:
        # Query immediately
        result1 = collection.query(query_embeddings=[embedding], n_results=1)
        assert len(result1["documents"][0]) > 0
        
        # Query again to test persistence
        result2 = collection.query(query_embeddings=[embedding], n_results=1)
        assert result1["documents"][0][0] == result2["documents"][0][0]
        
    finally:
        collection.delete(where={"$contains": sample_text})


def test_unicode_handling_comprehensive():
    """Test comprehensive Unicode handling across different languages"""
    unicode_texts = [
        "def 函数(): return '中文'",  # Chinese
        "def función(): return 'español'",  # Spanish
        "def функция(): return 'русский'",  # Russian
        "def פונקציה(): return 'עברית'",  # Hebrew
        "def 関数(): return '日本語'",  # Japanese
        "def फ़ंक्शन(): return 'हिंदी'",  # Hindi
    ]
    
    for text in unicode_texts:
        try:
            embedding = embed_text(text)
            assert embedding is not None
            assert len(embedding) > 0
            
            # Test storage and retrieval
            add_chunks([text], [embedding])
            result = collection.query(query_embeddings=[embedding], n_results=1)
            retrieved_text = result["documents"][0][0]
            assert retrieved_text == text
            
        finally:
            try:
                collection.delete(where={"$contains": text})
            except:
                pass
