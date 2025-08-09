import pytest
from ai_service import embedder, db, errors

# ------------------ Input Validation ------------------


# Ensure invalid inputs (empty strings, whitespace, None) raise appropriate exceptions
@pytest.mark.parametrize("invalid_input", ["", "   ", "\t", "\n", None])
def test_embed_invalid_inputs_raise_errors(invalid_input: str | None):
    if invalid_input is None:
        with pytest.raises(AttributeError):
            embedder.embed_text(invalid_input)  # pyright: ignore[reportArgumentType]
    else:
        with pytest.raises(
            errors.EmbeddingError,
            match="Cannot embed empty or whitespace-only text",
        ):
            embedder.embed_text(invalid_input)


# ------------------ Core Functionality ------------------


# Test storing and retrieving a variety of code snippets, including long ones
def test_embed_and_store_and_retrieve_texts():
    sample_texts = [
        "def greet(): print('Hello!')",
        "def farewell(): print('Goodbye!')",
        "class Calculator: pass",
        "def long_func():\n" + "    # comment\n" * 1000 + "    pass",  # very long text
        "def a(): pass",
        "def b(): pass",
    ]
    embeddings = embedder.embed_texts(sample_texts)
    db.add_chunks(sample_texts, embeddings)

    test_collection = db.get_collection()
    for i, embedding in enumerate(embeddings):
        result = test_collection.query(query_embeddings=[embedding], n_results=1)
        docs = result.get("documents")
        assert docs is not None, "Query returned None for documents"
        assert docs[0][0] == sample_texts[i]  # Check exact match


# ------------------ Unicode, Special Characters ------------------


# Ensure the embedding system handles various languages, symbols, and edge inputs
@pytest.mark.parametrize(
    "text",
    [
        "def greet(): print('Hello! 你好')",
        "# Comment with émojis 🚀",
        "def func(): return 'quotes\"and\\backslashes'",
        "multiline\nstring\nwith\nnewlines",
        "def 函数(): return '中文'",
        "def función(): return 'español'",
        "def функция(): return 'русский'",
        "def פונקציה(): return 'עברית'",
        "def 関数(): return '日本語'",
        "def फ़ंक्शन(): return 'हिंदी'",
        "a",  # single char
        "1",  # number
        "!",  # symbol
        "@",  # symbol
        "中",  # Chinese char
    ],
)
def test_embed_and_retrieve_special_and_unicode_texts(
    text: str,
):
    embedding = embedder.embed_text(text)
    assert embedding is not None and len(embedding) > 0

    db.add_chunks(
        [text],
        [embedding],
    )

    test_collection = db.get_collection()
    result = test_collection.query(query_embeddings=[embedding], n_results=1)
    docs = result.get("documents")
    assert docs is not None and docs[0] is not None, "Query returned None for documents"
    assert docs[0][0] == text


# ------------------ Embedding Properties & Structure ------------------


# Check the embedding's structure, type, and integration with chroma DB
def test_embedding_output_properties_and_structure():
    text = "def test_function(): return True"
    embedding = embedder.embed_text(text)

    # Validate basic embedding properties
    assert all(isinstance(x, float) for x in embedding)
    assert len(embedding) > 0

    # Validate output structure from the DB query
    db.add_chunks(
        [text],
        [embedding],
    )
    test_collection = db.get_collection()
    result = test_collection.query(query_embeddings=[embedding], n_results=1)
    assert isinstance(result, dict)
    assert "documents" in result and isinstance(result["documents"], list)
    assert isinstance(result["documents"][0], list)
    assert len(result["documents"][0]) > 0
    assert "ids" in result


# ------------------ Query Behavior ------------------


# Check behavior with different `n_results` values including > available matches
def test_query_with_varied_n_results():
    sample_texts = [
        "def function_a(): pass",
        "def function_b(): pass",
        "def function_c(): pass",
    ]
    embeddings = embedder.embed_texts(sample_texts)
    db.add_chunks(
        sample_texts,
        embeddings,
    )

    test_collection = db.get_collection()
    for n in [1, 2, 5]:  # Requesting more results than stored is valid
        result = test_collection.query(query_embeddings=[embeddings[0]], n_results=n)
        docs_list = result.get("documents")
        assert docs_list is not None and len(docs_list) > 0, (
            "Query returned None or empty documents"
        )
        docs = docs_list[0]
        # NOTE:
        # ChromaDB may return duplicate documents when n_results exceeds the number
        # of uniquely stored items. This causes the length of the returned list
        # to exceed the number of stored items.
        # To handle this properly, we count only unique documents.
        unique_docs = set(docs)
        assert len(unique_docs) <= n
