# Consultant Profile

A small, standalone building block of an internal tool for consultant profiles: one
profile with its career stations, education, skills and reference projects, served by a
FastAPI backend and shown by a Next.js page. Five example profiles ship as fixtures in
`fixtures/profiles/`.

## Start

```bash
docker compose up --build
```

| | |
| --- | --- |
| Frontend | <http://localhost:3000> |
| API | <http://localhost:8000/api/v1/profiles> |
| Swagger UI | <http://localhost:8000/docs> |
| Health | <http://localhost:8000/api/v1/health> |

The backend loads the fixtures at start-up and keeps every change in memory. Edit a fixture,
then `docker compose restart backend`.

Without Docker, each part runs on its own. The backend needs [uv](https://docs.astral.sh/uv/)
(it fetches Python 3.13 itself), the frontend Node 24 with pnpm (`corepack enable`):

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend && pnpm install && pnpm dev
```

## Checks

Backend, in this order, from `backend/`:

```bash
uv run ruff check . && uv run mypy app && uv run pytest && uv run ruff format .
```

`pytest` measures coverage on the services and repositories and fails below 85 %
(`fail_under` in `pyproject.toml`). Frontend, from `frontend/`:

```bash
pnpm lint && pnpm type-check && pnpm test && pnpm build
```

On a machine without uv or Node, the same checks run in Docker:

```bash
docker compose run --build --rm backend-checks
```

```bash
docker compose run --build --rm frontend-checks
```

## Structure

```text
backend/
  app/
    api/endpoints/     HTTP only: profile_management.py, collections.py, health.py
    core/              container.py (DI), settings.py, exceptions.py, error_handling.py, logging.py
    models/            profile.py (the domain), responses.py, base.py, enums.py
    repositories/      interfaces.py, profile_repository.py (the in-memory store)
    services/          profile_service.py, entity_collection_service.py, base_entity_service.py
  tests/               conftest.py, utils/profile_factory.py, unit tests of services, repository and API
frontend/
  app/                 layout, the profile list (/) and the profile page (/profiles/[id])
  components/          profiles/ (profiles-table, profile-view, entity-card) and the shadcn primitives under shadcn/ui
  lib/                 api/profiles.ts (the backend calls), format.ts, env.ts
  models/domain.ts     the types as the backend serves them
fixtures/profiles/     the five example profiles, one JSON document each
docker-compose.yml     backend, frontend and the two check runners
```

## API

All routes sit under `/api/v1`; the generated schema at `/docs` is the reference.

| Route | |
| --- | --- |
| `GET /profiles` | the profile overviews, paginated with `limit` and `offset` |
| `GET /profiles/{id}` | one complete profile, with the computed fields |
| `PUT /profiles/{id}/work-experience/{item_id}` | replace one entry; likewise `education`, `projects`, `skill-categories` |
| `GET /health` | the service and its store |

## Conventions

- **Layers**: endpoints → services → repositories → store. Endpoints handle HTTP only and
  never catch a domain exception; services hold the behaviour; repositories work with
  `dict[str, Any]` and know no models.
- **Errors** are domain exceptions (`core/exceptions.py`) mapped centrally to status codes
  in `core/error_handling.py`.
- **Dependency injection** uses `functools.lru_cache` singletons in `core/container.py`;
  the `get_*_di()` functions are what `Depends()` takes.
- **Sub-collections** (work experience, education, projects, skill categories) are one
  `EntityCollectionService` parameterised by a `CollectionSpec`, routed by the
  `COLLECTION_ROUTES` table. Only entities with behaviour of their own get a service.
- **Models**: Pydantic v2. Computed fields (`full_name`, `is_current_position`,
  `duration_months`, `missing_fields`) are derived on read and rejected as input. The
  fields an entry needs are listed in `MANDATORY`; they are typed optional because an
  import may store a profile with gaps. `Profile.missing_fields` names them, the overview
  flags the profile as `incomplete`, and every write through the API requires them.
- **Store**: production uses Cosmos DB, partitioned on `tenant_id`; the repository stamps
  the tenant and scopes every read, so models and services never see it. This block keeps
  the same `IProfileRepository` interface over an in-memory dict and has no query engine:
  `query()` returns every document.
- **Check order**: `ruff check`, `mypy app`, `pytest`, `ruff format`.
- **Frontend**: the pages render on the server and fetch the backend from there
  (`lib/api/profiles.ts`); the browser never calls the backend. The list is a table of
  overviews; the profile page shows the executive summary with its figures, then every
  entry as a card with its bullet points (`components/profiles/entity-card.tsx`). Design
  tokens and fonts live in `app/global.css`; `components/shadcn/ui/` holds generated
  shadcn primitives.

## Entry points

- `backend/app/models/profile.py`
- `backend/app/services/profile_service.py`
- `backend/app/api/endpoints/profile_management.py`
- `backend/tests/unit/services/test_profile_service.py`
- `fixtures/profiles/`

## Configuration

Nothing is required. Optional settings go into a `.env` at the repository root
(`.env.example`); `docker compose` hands the file to the backend, and the backend reads it
directly when it runs outside Docker. The backend ignores variables it does not know; a
new one is a field in `backend/app/core/settings.py`. The frontend reads only
`BACKEND_URL` (default `http://127.0.0.1:8000`; `docker-compose.yml` sets it).

## AI APIs

Using an AI API is allowed. Bring your own key through an environment variable in `.env`,
or work with mocked responses. `docker compose up` and all checks above must keep running
without a key and without network access.
