# =============================================================================
# MULTI-STAGE PRODUCTION DOCKERFILE (VITE BUILD + NGINX RUNTIME)
#
# STAGE 1 (builder)  : Build static assets with Node/Vite
# STAGE 2 (runtime)  : Serve static assets via unprivileged NGINX and proxy /api
# =============================================================================

# =============================================================================
# STAGE 1 (builder) - BEGIN
# =============================================================================
FROM node:22.20.0-alpine AS builder

# Set working directory for the build process
WORKDIR /app

# Copy dependency files first (better caching)
COPY package.json package-lock.json ./
RUN npm ci --silent

# Copy source
COPY . .

# Build-time config for Vite (baked into the JS bundle).
# Default to same-origin /api and let NGINX proxy it to the backend.
ARG VITE_BACKEND_API_URL=/api
ENV VITE_BACKEND_API_URL=${VITE_BACKEND_API_URL}

# Build production bundle
RUN npm run build

# =============================================================================
# STAGE 2 (runtime) - BEGIN
# =============================================================================
FROM nginx:1.27-alpine3.20

# Add image metadata
LABEL org.opencontainers.image.description="AI Code Explorer - React/TypeScript frontend served by NGINX for GitHub repository upload and interactive code Q&A"

# Runtime defaults (Railway injects PORT; BACKEND_URL should be set per environment)
ENV PORT=5173
ENV BACKEND_URL=http://127.0.0.1:8080

# Copy NGINX configuration template for runtime variable substitution
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy the built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose the default PORT (5173). This is documentation only; the actual
# listening port is controlled by the PORT env var and may be overridden.
EXPOSE 5173

# Debug: Show environment variables and rendered config at startup
RUN echo '#!/bin/sh' > /docker-entrypoint.d/99-debug.sh && \
    echo 'echo "=== DEBUG: Environment Variables ==="' >> /docker-entrypoint.d/99-debug.sh && \
    echo 'echo "PORT=${PORT}"' >> /docker-entrypoint.d/99-debug.sh && \
    echo 'echo "BACKEND_URL=${BACKEND_URL}"' >> /docker-entrypoint.d/99-debug.sh && \
    echo 'echo "=== DEBUG: Rendered NGINX Config ==="' >> /docker-entrypoint.d/99-debug.sh && \
    echo 'cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "Config not yet rendered"' >> /docker-entrypoint.d/99-debug.sh && \
    chmod +x /docker-entrypoint.d/99-debug.sh

# Healthcheck: Request index.html directly (static file, no React initialization)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD wget -q -O - "http://localhost:${PORT}/index.html" >/dev/null 2>&1 || exit 1