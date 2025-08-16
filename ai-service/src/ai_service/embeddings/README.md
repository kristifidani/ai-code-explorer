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

Our transformer setup uses a singleton pattern with automatic device detection for optimal performance:

```python
@lru_cache(maxsize=1)
def get_model(trust_remote_code: bool = False) -> SentenceTransformer:
    model_name = utils.get_env_var(constants.EMBEDDING_MODEL)
    device = _get_device()

    return SentenceTransformer(
        model_name_or_path=model_name,
        device=device,
        trust_remote_code=trust_remote_code,
        cache_folder=None,
    )
```

**Configuration Parameters:**

- **`model_name_or_path`**: The previous mentioned model retrieved from environment variable `EMBEDDING_MODEL`.
- **`device`**: Automatically detects and uses best available hardware: `CUDA` → `MPS` → `CPU`.
- **`trust_remote_code`**: Set to `False` by default for security, but might be required for some specialized code models.
- **`cache_folder`**: Uses default HuggingFace cache location for model storage.
- **`@lru_cache(maxsize=1)`**: Ensures single model instance per process, preventing memory waste from repeated loading.

## Encoding Configuration

Our encoding system uses context-aware methods with automatic fallback for maximum compatibility:

```python
# For documents (during ingestion)
embeddings = model.encode_document(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    batch_size=32,
    precision="float32",
    show_progress_bar=False,
    device=None,
)

# For queries (during search)
embeddings = model.encode_query(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    batch_size=32,
    precision="float32",
    show_progress_bar=False,
    device=None,
)
```

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

**Code Understanding Improvements:**

- **Intelligent Text Chunking:** Split large files at logical boundaries (functions, classes, modules) rather than arbitrary character limits.
- **Context-Preserving Preprocessing:** Maintain code structure and comments during embedding to improve semantic understanding.
- **Multi-file Context:** Consider file relationships and imports when embedding for better code comprehension.

**Performance Improvements:**

- **Adaptive Batch Sizing:** Dynamic batch sizes based on available GPU memory and text length.
- **Dimension Optimization:** Configurable output dimensions (768→512→256) for speed/storage trade-offs based on use case.

**Flow Improvements:**

- **Incremental Embedding:** Only re-embed changed code sections rather than entire files.
- **Caching Strategy:** Implement file-level embedding cache with content hash validation.
- **Error Recovery:** Better handling of malformed code and encoding failures with graceful degradation.

**Note:** Our focus is on practical optimizations for code understanding and embedding efficiency. We avoid benchmarking multiple models or training custom models, instead concentrating on optimizing the current pipeline for better performance and accuracy.
