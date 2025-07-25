from ai_service.db import add_chunks, collection
from ai_service.embedder import embed_text

from ai_service.ollama_client import chat_with_ollama

from .exceptions import AIServiceError


def main() -> None:
    code = """
hello world 2
"""
    try:
        print("Generating embedding for code sample...")
        embedding = embed_text(code)

        print("Storing code chunk in database...")
        add_chunks([code], [embedding])
        print("Stored documents in DB:")
        print(collection.peek())

        # Example chat with Ollama
        response = chat_with_ollama("Say hello to the world!")
        print("Ollama response:", response)
    except AIServiceError as e:
        print(f"AI Service error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
