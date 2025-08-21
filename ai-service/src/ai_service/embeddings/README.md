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

## Selected Model: `jinaai/jina-embeddings-v2-base-code`

**Why this model?**

- **Code-specialized with wide language coverage & long context**
It's trained specifically on source code _(via GitHub)_ and supports _30 programming languages_, ideal for exploring diverse, multi-language repositories. It can process up to _8,192_ tokens, allowing you to embed entire files or large code regions in a single pass. Critical for context-aware retrieval in big codebases.
- **High performance on code-specific benchmarks**
With just ~161 million parameters (~307 MB), it remains compact and efficient—so embedding large corpora is practical even on moderate hardware.
- **Plug-and-play integration and ecosystem-friendly**
Designed to work seamlessly with SentenceTransformers (and frameworks like Haystack, LlamaIndex), it supports mean-pooling and “trust_remote_code” loads for quick implementation in embedding pipelines.

More information about this model can be found on [Hugging Face](https://huggingface.co/jinaai/jina-embeddings-v2-base-code).

## Transformer Configuration

- **`model_name_or_path`**: The previous mentioned model retrieved from environment variable `EMBEDDING_MODEL`.
- **`device`**: Automatically detects and uses best available hardware: `CUDA` → `MPS` → `CPU`.
- **`trust_remote_code`**: Set to `False` by default for security, but might be required for some specialized code models.
- **`cache_folder`**: Uses default HuggingFace cache location for model storage.

## Encoding Configuration

Our encoding system uses context-aware methods with automatic fallback for maximum compatibility.

**Context-Aware Encoding:**

- Uses `encode_document()` for code files during ingestion (`is_query=False`).
- Uses `encode_query()` for user search queries (`is_query=True`).
- Automatically falls back to default `encode()` if specialized methods are unavailable.

**Configuration Parameters:**

- **`convert_to_numpy=True`**: Returns NumPy arrays for ChromaDB compatibility and efficient storage.
- **`normalize_embeddings=True`**: Converts to unit vectors enabling fast dot-product similarity calculations.
- **`batch_size=32`**: Fixed batch size that balances memory usage and processing speed.
- **`precision="float32"`**: Full precision for maximum accuracy in similarity calculations.
- **`show_progress_bar=False`**: Disabled by default to reduce overhead, automatically enabled for large batches.
- **`device=None`**: Uses device configured during model loading (inherits from transformer setup).

## Possible Future Optimizations

- **Intelligent Text Chunking:** Split large files at logical boundaries (functions, classes, modules) rather than arbitrary character limits.
- **Context-Preserving Preprocessing:** Maintain code structure and comments during embedding to improve semantic understanding.
- **Multi-file Context:** Consider file relationships and imports when embedding for better code comprehension.
- **Dimension Optimization:** Configurable output dimensions (768→512→256) for speed/storage trade-offs based on use case.
- **Incremental Embedding:** Only re-embed changed code sections rather than entire files.
- **Caching Strategy:** Implement file-level embedding cache with content hash validation.
