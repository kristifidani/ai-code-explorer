# =============================================================================
# MULTI-STAGE DEVELOPMENT DOCKERFILE FOR REACT FRONTEND
# =============================================================================
# Stage 1: Install dependencies with full Node.js
# Stage 2: Run Vite dev server with minimal Node.js
# =============================================================================

ARG NODE_BASE=22.12-alpine

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

# Install all dependencies (including dev dependencies for Vite)
RUN npm ci --silent

# =============================================================================
# STAGE 2: DEVELOPMENT RUNTIME
#
# Start fresh with minimal Node.js image and only copy what's needed
# to run the Vite dev server.
# =============================================================================

FROM node:${NODE_BASE}

# Install curl for healthcheck
RUN apk add --no-cache curl

# Set working directory
WORKDIR /app

# Copy node_modules from builder (already installed)
COPY --from=builder /app/node_modules ./node_modules

# Copy package.json for npm scripts
COPY package.json package-lock.json ./

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=20s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173 || exit 1

# Run Vite dev server (bind to all interfaces for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]