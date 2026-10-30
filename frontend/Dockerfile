# syntax=docker/dockerfile:1
# Build context is the repository root, like the backend's.
FROM node:24-trixie-slim AS base

WORKDIR /app
# corepack takes the pnpm version from packageManager in package.json, so the
# image and local installs agree.
RUN corepack enable

# pnpm-workspace.yaml carries the build-script approvals; without it the install
# stops with ERR_PNPM_IGNORED_BUILDS.
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# --- Checks: lint, types and tests on the sources ----------------------------
# `docker compose run --build --rm frontend-checks`
FROM base AS checks
COPY frontend/ ./
CMD ["sh", "-c", "pnpm lint && pnpm type-check && pnpm test"]

# --- Build: the standalone server --------------------------------------------
FROM base AS build
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# --- Runtime ------------------------------------------------------------------
FROM node:24-trixie-slim AS runtime

WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
