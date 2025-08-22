# Embeddings Layer

The embeddings layer converts code and natural language queries into high-dimensional vectors that capture semantic meaning. This enables similarity search and code understanding capabilities.

## How Embeddings Work

**Transformation Example:**

```text
Input Code:
"def calculate_sum(a, b): return a + b"

↓ (Embedding Model Processing) ↓

Output Vector:
[0.23, -0.15, 0.87, 0.42, -0.63, 0.91, ...]  # 768 dimensions
```

**What happens during transformation:**

1. **Tokenization:** Code is split into meaningful tokens (keywords, identifiers, operators).
2. **Semantic Analysis:** Model understands the function's purpose (mathematical operation, addition).
3. **Vector Generation:** Creates a 768-dimensional vector that captures the code's meaning.
4. **Normalization:** Vector is normalized to unit length for efficient similarity comparisons.

**Why this is powerful:**

- Similar code functions will have similar vectors (close in vector space).
- Search query "add two numbers" will be close to the function vector.
- Enables semantic search beyond exact keyword matching.

## Model Selection

### Default Model: `sentence-transformers/all-MiniLM-L6-v2`

**Current default choice for resource efficiency:**

- **Lightweight & Fast**: Only ~23MB model size, fits comfortably on GPUs with 2GB+ memory.
- **Good Performance**: 384-dimensional embeddings that work well for code similarity.
- **Wide Compatibility**: Works on CPU, GPU, and low-resource environments.
- **Quick Setup**: Fast download and initialization times.

Depending on the resources, you can choose more optimal models like [jinaai/jina-embeddings-v2-base-code](https://huggingface.co/jinaai/jina-embeddings-v2-base-code) which is specialized in code embeddings and trained on Github repositories.

## Transformer Configuration

Minimalistic configuration for this MVP:

- **`model_name_or_path`**: Model retrieved from environment variable `EMBEDDING_MODEL`.
- **`trust_remote_code`**: Set to `False` by default for security reasons, but might be required for some specialized code models.
- **`cache_folder`**: Uses default HuggingFace cache location for model storage.

Check the `SentenceTransformer` class implementation for more configuration options.

## Encoding Configuration

Our encoding system uses context-aware methods with automatic fallback for maximum compatibility.

**Context-Aware Encoding:**

- Uses `encode_document()` for code files during ingestion (`is_query=False`).
- Uses `encode_query()` for user search queries (`is_query=True`).
- Automatically falls back to default `encode()` if specialized methods are unavailable.

**Configuration Parameters:**

- **`convert_to_numpy=True`**: Returns NumPy arrays for ChromaDB compatibility and efficient storage.
- **`normalize_embeddings=True`**: Converts to unit vectors enabling fast similarity calculations.
- **`batch_size=32`**: Default batch size that balances memory usage and processing speed.
- **`precision="float32"`**: Default precision for maximum accuracy in similarity calculations.
- **`show_progress_bar=False`**: Disabled by default to reduce overhead.

## Possible Future Optimizations

- **Enhanced Code Models:** Upgrade to specialized code embedding models like `jinaai/jina-embeddings-v2-base-code` trained specifically on GitHub repositories.
- **Dimension Optimization:** Configurable output dimensions (768→512→256) for speed/storage trade-offs based on use case.
- **Incremental Embedding:** Only re-embed changed code sections rather than entire files.
- **Caching Strategy:** Implement file-level embedding cache with content hash validation.
