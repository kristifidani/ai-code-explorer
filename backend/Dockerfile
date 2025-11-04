# =============================================================================
# MULTI-STAGE PRODUCTION DOCKERFILE
# =============================================================================
# Stage 1: Build the binary with full Rust toolchain
# Stage 2: Runtime image with only necessary files

ARG RUST_BASE=1.90-slim

# =============================================================================
# STAGE 1: BUILDER
#
# This stage contains all the tools needed to build/compile the Rust binary
# but won't be included in the final production image.
# =============================================================================

FROM rust:$RUST_BASE AS builder

# Install build dependencies
# pkg-config: Helper tool for compiling applications and libraries
# libssl-dev: OpenSSL development files needed for HTTPS support
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for the build process
WORKDIR /app

# Copy only dependency files first (for better Docker layer caching)
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY bin/ ./bin/
COPY src/ ./src/

# Build the application in release mode
RUN cargo build --release

# =============================================================================
# STAGE 2: PRODUCTION STAGE
#
# Start fresh with a (Minimal Debian).
# =============================================================================

FROM debian:bookworm-slim

# Install only runtime dependencies (no build tools)
# ca-certificates: For HTTPS connections
# curl: needed for healthcheck
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    curl \
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

# Copy only the compiled binary from builder stage
COPY --from=builder /app/target/release/rest-api /app/rest-api

# Set ownership for the binary
RUN chown app:app /app/rest-api

# SWITCH TO NON-ROOT USER
USER app

# Expose port 8080 (this is just documentation, doesn't actually open the port)
EXPOSE 8080

# Add healthcheck instruction for self-documenting image
# This provides a default healthcheck when running outside docker-compose
HEALTHCHECK --interval=30s --timeout=15s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the backend service
CMD ["/app/rest-api"]
