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
FROM nginxinc/nginx-unprivileged:1.29.3-alpine3.22

# Add image metadata
LABEL org.opencontainers.image.description="AI Code Explorer - React/TypeScript frontend served by NGINX for GitHub repository upload and interactive code Q&A"

# Runtime defaults (Railway injects PORT; BACKEND_URL should be set per environment)
ENV PORT=5173
ENV BACKEND_URL=http://localhost:8080

# Copy NGINX configuration template for runtime variable substitution
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy the built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose the default PORT (5173)
EXPOSE ${PORT}

# Healthcheck: Request index.html directly (static file, no React initialization)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD wget -q -O - "http://localhost:${PORT}/index.html" >/dev/null 2>&1 || exit 1