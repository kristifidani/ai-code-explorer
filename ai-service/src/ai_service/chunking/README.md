# Code Chunking Strategy

The chunking layer is responsible for **preprocessing** code files into manageable segments before embedding. This is a critical step that determines how well the semantic search system can find relevant code.

## Why Chunking Matters

**The Problem:** Whole files are too large and unfocused for effective embedding:

- Large files exceed embedding model context windows.
- Mixed content (imports + functions + tests) creates noisy embeddings.
- Poor retrieval granularity (getting entire files instead of relevant functions).

**The Solution:** Break files into meaningful, focused chunks:

- Each chunk contains related code (reasonable scope).
- Chunks have overlap for context continuity.
- Manageable size for embedding models (~30 lines).

## Current Implementation: Simple Line-Based Chunking

Our current strategy prioritizes **simplicity and reliability** over complexity:

### How It Works

```python
# Example: 100-line file becomes 4 overlapping chunks
File (100 lines) → Chunks:
- Chunk 1: lines 1-30
- Chunk 2: lines 26-55    # 5-line overlap with previous
- Chunk 3: lines 51-80    # 5-line overlap with previous
- Chunk 4: lines 76-100   # 5-line overlap with previous
```

### Configuration

```python
chunk_size = 30    # Target lines per chunk (optimal for embedding models)
overlap = 5        # Lines shared between chunks (maintains context)
min_content = 3    # Minimum non-empty lines required for a chunk
```

### Chunk Format

Each chunk includes helpful context headers:

```text
# File: handlers/answer.py
# Chunk: lines 15-44

def answer_question(user_question: str, repo_url: str) -> str:
    try:
        set_repo_context(repo_url)
        query_embedding = embed_query(user_question)
        # ... rest of function
```

## What We've Solved

### Context Size Management

- **Before:** Entire files (sometimes 1000+ lines) as single chunks.
- **After:** Manageable 30-line chunks with good context.

### Retrieval Granularity

- **Before:** Getting whole files when asking specific questions.
- **After:** Getting focused code segments relevant to the query.

### Performance Improvement

- **Before:** 60+ second response times due to massive context.
- **After:** 15-25 second response times with focused context.

### Universal Language Support

- **Before:** Would need custom parsers for each language.
- **After:** Single algorithm works for Python, Rust, JavaScript, etc.

## Future Optimization Opportunities

### 1. **Semantic-Aware Chunking**

Instead of line-based, chunk by code structure:

- Functions/methods as individual chunks.
- Classes with their methods.
- Import blocks as separate chunks.

**Trade-off:** More complexity vs better semantic boundaries.

### 2. **Language-Specific Optimizations**

- Python: Chunk by function/class definitions.
- Rust: Chunk by impl blocks, struct definitions.
- JavaScript: Chunk by function/component boundaries.

**Trade-off:** Maintenance overhead vs specialized optimization.

### 3. **Context-Aware Chunking**

- Include related code (function + its dependencies).
- Maintain file structure information.
- Preserve comment-code relationships.

**Trade-off:** Larger chunks vs better context preservation.

### 4. **Adaptive Chunk Sizing**

- Small chunks for dense code (functions).
- Larger chunks for sparse code (configuration files).
- Dynamic sizing based on code complexity.

**Trade-off:** Algorithm complexity vs optimized chunk sizes.
