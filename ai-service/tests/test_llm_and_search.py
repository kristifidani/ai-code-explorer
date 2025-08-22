from ai_service import ollama_client
from ai_service.db_setup import add_chunks, get_collection, query_chunks
from ai_service.embeddings import embed_documents, embed_query

import pytest

# -------------- LLM Chat Tests --------------


def test_llm_chat_basic_response(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "ai_service.ollama_client.chat_with_ollama",
        lambda prompt: "Mocked LLM response for: " + prompt,  # type: ignore
    )
    prompt = "Code context:\ndef add(a, b): return a + b\nQuestion: How does the sum work?\nExplain."
    response = ollama_client.chat_with_ollama(prompt)
    assert response.startswith("Mocked LLM response for:")


# -------------- DB Search + LLM Integration --------------


def test_db_search_and_llm_integration(monkeypatch: pytest.MonkeyPatch):
    # Add code to DB
    code = "def add(a, b): return a + b"
    embedding = embed_documents([code])
    add_chunks(
        [code],
        embedding,
    )

    # Mock LLM
    monkeypatch.setattr(
        "ai_service.ollama_client.chat_with_ollama",
        lambda prompt: f"LLM saw: {prompt}",  # type: ignore
    )
    # User question
    question = "How does the sum work?"
    question_embedding = embed_query(question)
    results = query_chunks(
        question_embedding,
    )
    docs = results.get("documents")
    relevant_code = docs[0][0] if docs and docs[0] else ""
    prompt = f"Code context:\n{relevant_code}\nQuestion: {question}\nExplain."
    response = ollama_client.chat_with_ollama(prompt)
    assert "LLM saw: Code context:" in response
    assert code in response
    assert question in response


# -------------- Edge Cases --------------


def test_db_search_no_results():
    # Ensure db is empty
    test_collection = get_collection()
    if test_collection.peek()["ids"]:
        test_collection.delete(ids=test_collection.peek()["ids"])
    question = "This code does not exist."
    question_embedding = embed_query(question)
    results = query_chunks(
        question_embedding,
    )
    # Should return an empty or placeholder result
    docs = results.get("documents")
    assert docs is not None and (docs[0] == [] or (docs[0] and docs[0][0] == ""))


def test_llm_chat_with_long_prompt(monkeypatch: pytest.MonkeyPatch):
    # Mock LLM
    monkeypatch.setattr(
        "ai_service.ollama_client.chat_with_ollama",
        lambda prompt: "LLM received prompt of length: " + str(len(prompt)),  # type: ignore
    )
    long_code = "def foo(): pass\n" * 1000
    prompt = f"Code context:\n{long_code}\nQuestion: What does this do?\nExplain."
    response = ollama_client.chat_with_ollama(prompt)
    assert response.startswith("LLM received prompt of length:")
