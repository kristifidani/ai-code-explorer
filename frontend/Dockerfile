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

# Install envsubst for runtime config templating
USER root
RUN apk add --no-cache gettext-envsubst

# Use nginxinc's built-in entrypoint envsubst hook.
# Any /etc/nginx/templates/*.template file is rendered to /etc/nginx/conf.d/*
# at container start. BACKEND_URL is injected at runtime (e.g. by Railway).
RUN rm -f /etc/nginx/conf.d/default.conf
COPY --chown=101:101 nginx.conf /etc/nginx/templates/default.conf.template
USER 101

# Copy the built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 8080 (this is just documentation, doesn't actually open the port)
EXPOSE 8080

# Add healthcheck instruction for self-documenting image
# This provides a default healthcheck when running outside docker-compose
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD wget -q -O - http://localhost:8080/ >/dev/null 2>&1 || exit 1