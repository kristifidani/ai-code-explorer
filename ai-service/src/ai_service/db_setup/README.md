# Database Setup Layer

The database setup layer manages ChromaDB operations for storing and querying code embeddings. This module provides a clean abstraction over ChromaDB for the AI service.

## Why Vector Databases?

Traditional databases store exact data (text, numbers, dates), but AI applications need to work with **semantic similarity**. Vector databases solve this by storing and searching high-dimensional vectors that represent meaning.

### How Vector Databases Work

```text
1. Transform content into vectors (embeddings)
   "def calculate_sum(a, b): return a + b" → [0.23, -0.15, 0.87, ...]

2. Store vectors with metadata
   Vector Database: {vector, content, metadata}

3. Find similar content using vector similarity
   Query: "function that adds numbers" → [0.25, -0.12, 0.84, ...]
   Database finds closest vectors → Returns similar code functions
```

### ChromaDB: our vector database choice

**ChromaDB** is an open-source vector database designed for AI applications:

- **Simple to deploy** - No complex setup, works locally or in production
- **Similarity search** - Finds semantically similar content, not just exact matches
- **Collections** - Organize data by project/repository for isolation
- **Fast queries** - Optimized for vector similarity operations
- **Python-native** - Excellent integration with our Python stack

## Current Storage Flow

```python
# 1. Set repository context
set_repo_context("https://github.com/user/repo.git")

# 2. Store code chunks
chunks = ["def hello(): return 'world'", "class MyClass: pass"]
embeddings = embed_documents(chunks)  # From embeddings layer
add_chunks(chunks, embeddings)

# 3. Query for similar code
query_embedding = embed_query("function that returns string")
results = query_chunks(query_embedding, number_of_results=3)
```

## What Works Well

**Clean separation of concerns** - Each module has a single responsibility.
**Deduplication** - Prevents storing duplicate code chunks.
**Repository isolation** - Each repo gets its own collection.
**Batch operations** - Efficient handling of multiple chunks.
**Error handling** - Proper exception handling with custom errors.
**NumPy compatibility** - Handles ChromaDB version issues.

## Current Limitations & Future Improvements

### 1. **Limited Metadata**

**Current:** Only stores code content and embeddings
**Future Enhancement:**

```python
# Rich metadata structure
metadata = {
    "file_path": "src/handlers/ingest.py",
    "language": "python",
    "chunk_type": "function",  # function, class, file
    "function_name": "ingest_github_project",
    "line_start": 42,
    "line_end": 89,
    "github_url": "https://github.com/repo/blob/main/src/handlers/ingest.py#L42-L89"
}
```

### 2. **Limited Search Context**

**Current:** Only content-based similarity search
**Future Enhancement:**

- Metadata-filtered search (by language, file type, function name)
- Hybrid search combining content + metadata relevance
- Language-specific search optimizations

### 3. **Basic Hash Strategy**

**Current:** Simple content-based SHA256 hashing
**Future Enhancement:**

- Include metadata in hash for better uniqueness
- Handle code refactoring (similar content, different locations)
- Version-aware deduplication
