# =============================================================================
# MULTI-STAGE PRODUCTION DOCKERFILE
# =============================================================================
# Stage 1: Build dependencies and install packages
# Stage 2: Runtime image with only necessary files

ARG PYTHON_BASE=3.10-slim

# =============================================================================
# STAGE 1: BUILDER
#
# This stage contains all the tools needed to build/compile dependencies
# but won't be included in the final production image.
# =============================================================================

FROM python:$PYTHON_BASE AS builder

# Install build dependencies (compilers, git, etc.)
# These are needed to compile Python packages with C extensions (like numpy, torch)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc=4:14.2.0-1 \
    g++=4:14.2.0-1 \
    git=1:2.47.3-0+deb13u1 \
    && rm -rf /var/lib/apt/lists/*

# Install PDM (Python Dependency Manager)
RUN pip install --no-cache-dir pdm==2.25.9
# Disable update check for faster build
ENV PDM_CHECK_UPDATE=false

# Set working directory for the build process
WORKDIR /app

# Copy only dependency files first (for better Docker layer caching)
COPY pyproject.toml pdm.lock README.md ./

# Install dependencies using PDM defaults (creates .venv automatically)
RUN pdm install --check --prod --no-editable

# Copy source code (needed for the final stage)
COPY src/ ./src/

# =============================================================================
# STAGE 2: PRODUCTION STAGE
#
# Start fresh with a clean Python image.
# =============================================================================

FROM python:$PYTHON_BASE

# Install only runtime dependencies (no build tools)
# git: needed for GitPython package
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git=1:2.47.3-0+deb13u1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# SECURITY: CREATE NON-ROOT USER
# =============================================================================
# Running as root is a security risk. If the app gets compromised,
# the attacker won't have full system access
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Retrieve packages from build stage  
COPY --from=builder /app/.venv/ /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source code from builder
COPY --from=builder /app/src/ ./src/

# Set Python path so Python can find our modules
ENV PYTHONPATH=/app/src

# Production environment variables
# Tells app to run in production mode (no reload, quiet logs)
ENV ENVIRONMENT=production
# Force real-time stdout/stderr (essential for Docker logs)
ENV PYTHONUNBUFFERED=1
# Skip .pyc files (saves space, faster startup)
ENV PYTHONDONTWRITEBYTECODE=1

# Set ownership for source code
RUN chown app:app /app/src

# SWITCH TO NON-ROOT USER
USER app

# Expose port 8000 (this is just documentation, doesn't actually open the port)
EXPOSE 8000

# Set command/entrypoint, adapt to fit your needs
CMD ["python", "-m", "ai_service.main"]