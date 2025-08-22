def chunk_code_file(file_path: str, content: str) -> list[str]:
    """
    Code chunking strategy implementation for preprocessing files.

    This is the main chunking strategy that splits large code files
    into smaller, manageable segments for embedding and retrieval.
    """
    # Split file content into individual lines for processing
    lines = content.strip().split("\n")

    # Small files don't need chunking - return as single chunk
    if len(lines) < 20:
        return [_add_file_context(file_path, content, "complete-file")]

    chunks: list[str] = []
    chunk_size = 30  # Target lines per chunk
    overlap = 5  # Lines to overlap between chunks for context continuity

    # Create overlapping chunks by stepping through the file
    for i in range(0, len(lines), chunk_size - overlap):
        # Extract chunk_size lines starting from position i
        chunk_lines = lines[i : i + chunk_size]

        # Only create chunk if it has meaningful content (at least 3 non-empty lines)
        if len([line for line in chunk_lines if line.strip()]) >= 3:
            # Convert lines back to text content
            chunk_content = "\n".join(chunk_lines)
            # Create descriptive name showing line range
            chunk_name = f"lines {i+1}-{i+len(chunk_lines)}"
            # Add file context header and store the chunk
            chunks.append(_add_file_context(file_path, chunk_content, chunk_name))

    return chunks


def _add_file_context(file_path: str, chunk: str, chunk_name: str) -> str:
    """
    Add simple file context to a chunk.

    Args:
        file_path: Full path to the file
        chunk: Code content
        chunk_name: Simple chunk identifier

    Returns:
        Formatted chunk with context header
    """
    # Extract just the filename and parent folder for readability
    # e.g., "/long/path/to/src/handlers/answer.py" becomes "handlers/answer.py"
    path_parts = file_path.split("/")
    short_path = "/".join(path_parts[-2:]) if len(path_parts) >= 2 else path_parts[-1]

    # Create header with file info and chunk identifier, then add the actual code
    return f"# File: {short_path}\n# Chunk: {chunk_name}\n\n{chunk}"
