# syntax=docker/dockerfile:1

# -------- Build Stage --------
ARG NODE_VERSION=22.13.1
FROM node:${NODE_VERSION}-slim AS builder
WORKDIR /app

# Install OS dependencies for node-gyp etc (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 g++ make && \
    rm -rf /var/lib/apt/lists/*

# Copy package.json and package-lock.json for layer caching
COPY --link package.json ./
# If you use package-lock.json, copy it too (never copy .env or lock files from other package managers)
COPY --link package-lock.json ./

# Install dependencies (use npm ci for deterministic builds)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy all source files (excluding files in .dockerignore)
COPY --link . .

# Build Next.js app (outputs to .next)
RUN npm run build

# -------- Production Stage --------
FROM node:${NODE_VERSION}-slim AS final
WORKDIR /app

# Create non-root user
RUN groupadd --system appuser && useradd --system --gid appuser appuser

# Copy standalone output from builder (Next.js 13+ standalone mode)
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Set environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Expose Next.js port
EXPOSE 3000

# Change ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck: GET / every 30s, timeout 10s, 3 retries (using node instead of curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

# Start Next.js standalone server
CMD ["node", "server.js"]
