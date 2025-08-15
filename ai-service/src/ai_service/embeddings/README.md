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

## Encoding Configuration

```python
embeddings = model.encode_document(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    batch_size=32,
    precision="float32",
    show_progress_bar=True,
    device=None,
)
```

- **`convert_to_numpy=True`:** Returns NumPy arrays for ChromaDB compatibility.
- **`normalize_embeddings=True`:** Converts to unit vectors enabling fast dot-product similarity.
- **`batch_size=32`:** Balances memory usage and processing speed.
- **`precision="float32"`:** Full precision for maximum accuracy.
- **`show_progress_bar`:** Auto-displayed for batches >10 items.
- **`device=None`:** Uses device configured during model loading.

## Current Implementation

1. **Auto Device Detection** - Automatically detects and uses best available hardware: `CUDA` → `MPS` → `CPU`.

2. **Memory-Efficient Model Caching**
   - Single model instance per process using `@lru_cache(maxsize=1)`.
   - Prevents repeated model loading and saves memory.
   - Model stays in memory for entire application lifetime.

3. **Context-Aware Encoding**
   - Uses `encode_query()` for user search queries (`is_query=True`).
   - Uses `encode_document()` for code files during ingestion (`is_query=False`).
   - Automatically detects available methods with `hasattr()` checks.

4. **Production-Ready Configuration**
   - `trust_remote_code=False` but might be required for code-specific models.
   - `normalize_embeddings=True` for fast cosine similarity.
   - `convert_to_numpy=True` for ChromaDB compatibility.
   - `precision="float32"` for maximum accuracy.

5. **Batch Processing**
   - Fixed batch size of 32 for balanced speed/memory usage.
   - Progress bar display for user feedback. Default is `False` since it can add overhead.
   - Efficient handling of multiple texts simultaneously.

## Future Optimizations

### Performance Enhancements (Next Phase)

- **ONNX Backend:** 2-3x faster inference with `backend="onnx"`. Default is `torch`.
- **Adaptive Batch Sizing:** Dynamic batch sizes based on available GPU memory.
- **Dimension Truncation:** Configurable dimensions (768→256) for speed/storage trade-offs.

### Code Understanding Improvements (Later Phases)

- **Intelligent Chunking:** Split large files at logical boundaries (functions, classes)
- **Model Benchmarking:** Compare Jina vs CodeBERT vs other code-specific models
- **Domain Fine-tuning:** Train on your specific codebase patterns
