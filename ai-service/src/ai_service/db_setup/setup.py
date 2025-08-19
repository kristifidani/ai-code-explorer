import hashlib
import numpy as np
from ai_service import constants, utils, errors

# --- Handle ChromaDB NumPy compatibility ---
# ChromaDB may fail with newer NumPy versions >2.0 that removed np.float_
# This ensures backward compatibility by aliasing float_ to float64
if not hasattr(np, "float_"):
    np.float_ = np.float64  # type: ignore

import chromadb
from contextvars import ContextVar

# Set up ChromaDB client and persistent collection
chroma_path = utils.get_env_var(constants.CHROMA_STORE_PATH)
client = chromadb.PersistentClient(path=chroma_path)

_current_repo_url: ContextVar[str] = ContextVar("current_repo_url")


def set_repo_context(canonical_github_url: str) -> None:
    """Set the current repository URL context for all DB operations."""
    _current_repo_url.set(canonical_github_url)


def get_collection() -> chromadb.Collection:
    """Get or create a ChromaDB collection using the current repo context."""
    try:
        canonical_github_url = _current_repo_url.get()
    except LookupError as e:
        raise errors.DatabaseError.no_repo_context(e) from e

    url_hash = hashlib.sha256(canonical_github_url.encode("utf-8")).hexdigest()[:12]
    repo_name = canonical_github_url.split("/")[-1].replace(".git", "")
    collection_name = f"{repo_name}_{url_hash}"
    return client.get_or_create_collection(collection_name)
