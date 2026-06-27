# Directory Structure

> How backend code is organized in this project.

---

## Overview

The backend is a small FastAPI proxy under `pickora/api/`. It exists to keep the DashScope provider key on the server, validate a narrow AI-generation contract, and apply basic no-login abuse controls.

There is no layered application framework yet. Keep the structure intentionally flat unless a new feature proves that a split is needed.

---

## Directory Layout

```text
pickora/api/
├── app/
│   ├── main.py              # FastAPI app factory, middleware, routes, dependency wiring
│   ├── config.py            # Environment-backed settings and defaults
│   ├── schemas.py           # Pydantic request/response models and category literals
│   ├── dashscope_client.py  # DashScope prompt building, provider call, response parsing
│   └── rate_limit.py        # In-memory per-IP rate limiter
├── requirements.txt         # Pinned Python runtime dependencies
└── Dockerfile               # API container image
```

Deployment-level files live outside the API package:

- `pickora/docker-compose.yml` wires the API and frontend containers.
- `pickora/.env.example` documents environment variables with placeholders only.
- `pickora/deploy/nginx.conf` contains reverse-proxy configuration.

---

## Module Organization

- Define HTTP routes and request middleware in `pickora/api/app/main.py`.
  - Example: `create_app()` registers CORS, request-size middleware, `/health`, and `POST /api/generate-options`.
- Define request and response shapes in `pickora/api/app/schemas.py` using Pydantic models.
  - Example: `GenerateOptionsRequest` accepts only the fixed `Category` literal and sets `extra = "forbid"`.
- Keep environment parsing in `pickora/api/app/config.py`.
  - Example: `_read_int()` accepts only positive integers and falls back to defaults.
- Keep provider-specific logic out of route handlers.
  - Example: `pickora/api/app/dashscope_client.py` owns `build_prompt()`, `parse_options()`, and `generate_dashscope_options()`.
- Keep small reusable infrastructure helpers in dedicated modules.
  - Example: `pickora/api/app/rate_limit.py` contains the `RateLimiter` class.

Do not introduce a `services/`, `repositories/`, or `database/` layer until there is more than one real backend use case for it.

---

## Naming Conventions

- Python modules use `snake_case.py` (`dashscope_client.py`, `rate_limit.py`).
- Classes use `PascalCase` (`Settings`, `RateLimiter`, `GenerateOptionsRequest`).
- Functions and variables use `snake_case` (`get_settings`, `generate_dashscope_options`, `max_request_bytes`).
- Environment variables use upper snake case and are read only in settings/config code (`DASHSCOPE_API_KEY`, `FRONTEND_ORIGIN`).
- API paths are lowercase kebab-case under `/api` for product endpoints (`/api/generate-options`) and plain `/health` for health checks.

---

## Examples

- `pickora/api/app/main.py` is the reference for app wiring and route-level dependency injection.
- `pickora/api/app/schemas.py` is the reference for narrow public API contracts.
- `pickora/api/app/dashscope_client.py` is the reference for isolating external provider behavior from FastAPI route handlers.
- `pickora/api/app/rate_limit.py` is the reference for small, dependency-free backend helpers.

---

## Forbidden Patterns

- Do not place provider keys, tokens, or production secrets in source code, README examples, or frontend files.
- Do not let browser input become arbitrary provider prompts. Map fixed categories to server-owned prompts.
- Do not add persistent storage or an ORM for the current no-login product without a new design task.
- Do not create deep package layers for one endpoint; prefer the current flat modules until duplication appears.
