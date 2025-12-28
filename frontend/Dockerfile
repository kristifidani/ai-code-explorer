# =============================================================================
# MULTI-STAGE DEVELOPMENT DOCKERFILE FOR REACT FRONTEND
# =============================================================================
# Stage 1: Install dependencies with full Node.js
# Stage 2: Run Vite dev server with Node.js runtime
# =============================================================================

ARG NODE_BASE=22.12.0-alpine

# =============================================================================
# STAGE 1: BUILDER
#
# This stage installs all dependencies including dev dependencies
# but won't be included in the final production image.
# =============================================================================

FROM node:${NODE_BASE} AS builder

# Set working directory for the build process
WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY package.json package-lock.json ./

# Install all dependencies
RUN npm ci --silent

# =============================================================================
# STAGE 2: DEVELOPMENT RUNTIME
#
# Start fresh with a clean Node.js image and only copy what's needed.
# =============================================================================

FROM node:${NODE_BASE}

# Install runtime dependencies
# curl: needed for healthcheck
RUN apk add --no-cache curl

# =============================================================================
# SECURITY: CREATE NON-ROOT USER
# =============================================================================
# Running as root is a security risk. If the app gets compromised,
# the attacker won't have full system access
RUN addgroup -S app && adduser -S -G app -h /home/app -s /bin/sh app

# Set working directory
WORKDIR /app

# Copy node_modules from builder (already installed) with ownership up-front (avoids slow/large chown layer)
COPY --from=builder --chown=app:app /app/node_modules ./node_modules

# Copy package.json for npm scripts with ownership up-front (avoids slow/large chown layer)
COPY --chown=app:app package.json package-lock.json ./

# Copy source code with ownership up-front (avoids slow/large chown layer)
COPY --chown=app:app . .

# SWITCH TO NON-ROOT USER
USER app

# Expose Vite dev server port
EXPOSE 5173

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=20s \
    CMD curl -f http://localhost:5173 || exit 1

# Run Vite dev server (bind to all interfaces for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]