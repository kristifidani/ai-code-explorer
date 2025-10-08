# Use Python 3.10 (matches your pyproject.toml)
FROM python:3.10-slim

# Set Python path so modules can be found
ENV PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install pdm==2.25.9

# Copy dependency files and source code
COPY pyproject.toml pdm.lock README.md ./
COPY src/ ./src/

# Configure PDM - keep venv but make it global
RUN pdm config venv.with_pip true && \
    pdm config python.use_venv false

# Install the dependencies and packages
RUN pdm install --prod

# Create directory for ChromaDB data
RUN mkdir -p /app/chroma_store

# Expose the port your app runs on
EXPOSE 8000

# Add a proper health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application using PDM
CMD ["pdm", "run", "start"]