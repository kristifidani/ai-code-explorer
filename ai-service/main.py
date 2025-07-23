from embedder import embed_text
from db import add_chunks, collection

code = """
hello world
"""

try:
    embedding = embed_text(code)
    add_chunks([code], [embedding])

    # List all stored items
    print("Stored documents in DB:")
    print(collection.peek())
except Exception as e:
    print(f"Error processing code: {e}")

