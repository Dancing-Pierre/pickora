# Database Guidelines

> Database patterns and conventions for this project.

---

## Overview

Pickora currently has **no database, ORM, migrations, or server-side persistence**. The product is intentionally no-login and self-deployable:

- `pickora/README.md` states that recent complete choice sessions are stored in browser `localStorage`.
- `pickora/api/requirements.txt` includes FastAPI, Uvicorn, HTTPX, and Pydantic only; there is no ORM or database driver.
- `pickora/api/app/rate_limit.py` keeps rate-limit buckets in process memory.
- `pickora/frontend/src/composables/useChoiceHistory.ts` is the only persistence implementation and writes to `localStorage`.

Treat the absence of a database as an explicit project constraint, not an unfinished layer.

---

## Query Patterns

There are no database queries in the current codebase.

When backend code needs data, use the existing sources:

- Request bodies validated by Pydantic models in `pickora/api/app/schemas.py`.
- Environment-backed settings from `pickora/api/app/config.py`.
- External provider responses parsed in `pickora/api/app/dashscope_client.py`.
- In-memory runtime state for low-value, non-critical controls such as `RateLimiter`.

Do not add ad hoc file persistence, SQLite, Redis, or an ORM as a shortcut for current features.

---

## Migrations

There is no migration system.

If a future requirement introduces server-side persistence, create a separate design task before implementation. That task must define:

- Storage engine and hosting assumptions.
- Schema ownership and naming conventions.
- Migration command and rollback strategy.
- How existing browser-local history should or should not migrate.
- Privacy expectations for a formerly no-login app.

---

## Naming Conventions

No table, column, or index naming conventions exist because there are no database objects.

For current persistence-like keys, follow the frontend localStorage convention instead:

- Use a product prefix and version suffix.
- Example: `pickora:history:v1` in `pickora/frontend/src/composables/useChoiceHistory.ts`.

---

## Common Mistakes

- Do not introduce a database just to store recent choices; the current contract is device-local history capped to five sessions.
- Do not rely on in-memory rate-limit data for durable enforcement; `RateLimiter` resets on process restart and is only a lightweight abuse-control measure.
- Do not document database-backed behavior in API or frontend specs until it exists in code.
- Do not persist provider responses server-side unless the product requirement changes and privacy/storage rules are designed first.
