from ai_service.db import add_chunks, collection
from ai_service.embedder import embed_text

code = """
hello world 2
"""


def main() -> None:
    try:
        print("Generating embedding for code sample...")
        embedding = embed_text(code)
        print("Storing code chunk in database...")
        add_chunks([code], [embedding])

        # List all stored items
        print("Stored documents in DB:")
        print(collection.peek())
    except (ValueError, RuntimeError) as e:
        print(f"Error processing code or embeddings: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
