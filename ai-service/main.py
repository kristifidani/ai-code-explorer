from embedder import embed_text
from db import add_chunks, collection

code = """
hello world 2
"""

try:
    embedding = embed_text(code)
    add_chunks([code], [embedding])

    # List all stored items
    print("Stored documents in DB:")
    print(collection.peek())
except (ValueError, RuntimeError) as e:
    print(f"Error processing code: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
