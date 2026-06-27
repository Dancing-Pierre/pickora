# Backend Quality Guidelines

> Code quality standards for backend development.

---

## Overview

The backend is a minimal FastAPI proxy for a public, no-login site. Quality is defined by keeping the API contract narrow, protecting provider credentials, returning predictable errors, and avoiding unnecessary infrastructure.

Current reference files:

- `pickora/api/app/main.py` for FastAPI app creation, middleware, CORS, route dependencies, and status-code behavior.
- `pickora/api/app/schemas.py` for Pydantic API contracts.
- `pickora/api/app/dashscope_client.py` for external-provider calls and response normalization.
- `pickora/api/app/rate_limit.py` for small dependency-free helpers.
- `pickora/api/app/config.py` for environment defaults.

---

## Scenario: Public AI Proxy Without User Accounts

### 1. Scope / Trigger

- Trigger: A public frontend needs AI-generated content, but provider keys must never reach browser code or a public repository.
- Applies when adding a small backend proxy for an external AI provider, especially on no-login public sites.

### 2. Signatures

- `POST /api/generate-options`
- Request model:
  ```python
  Category = Literal["food", "play", "movie"]

  class GenerateOptionsRequest(BaseModel):
      category: Category
      model_config = {"extra": "forbid"}
  ```
- Response model:
  ```python
  class GenerateOptionsResponse(BaseModel):
      category: Category
      options: list[str]
  ```

### 3. Contracts

- Request fields:
  - `category`: required, one of `food`, `play`, `movie`.
  - No other fields are accepted.
- Response fields:
  - `category`: echoes the accepted category.
  - `options`: exactly six normalized, non-empty strings for UI cards.
- Environment keys:
  - `DASHSCOPE_API_KEY`: optional at process start, but required for successful AI calls.
  - `DASHSCOPE_MODEL`: optional, defaults to `qwen-turbo`.
  - `FRONTEND_ORIGIN`: production CORS origin.
  - `AI_RATE_LIMIT_PER_MINUTE`: default `5`.
  - `AI_RATE_LIMIT_PER_HOUR`: default `30`.
  - `MAX_REQUEST_BYTES`: default `1024`.

### 4. Validation & Error Matrix

| Condition | Expected behavior |
| --- | --- |
| Missing AI key | `503`, controlled message, manual frontend flow remains usable |
| Category outside allowlist | `422` from request validation |
| Extra request field | `422` from `extra = "forbid"` |
| Oversized request | `413` |
| Invalid `Content-Length` | `400` |
| Rate limit exceeded | `429` with user-safe message |
| Provider auth failure | `502` with configuration message; never echo provider payload/key |
| Provider returns unparsable/non-six options | `502` controlled invalid-format error |

### 5. Good/Base/Bad Cases

- Good: `POST /api/generate-options` with `{"category":"food"}` returns exactly six short options.
- Base: No `DASHSCOPE_API_KEY` configured returns `503`; frontend can still manually draw.
- Bad: `{"category":"food","prompt":"anything"}` is rejected instead of becoming arbitrary prompt injection.

### 6. Tests Required

There is no committed backend test suite yet. For current changes, at minimum run:

```bash
cd pickora/api
python -m compileall app
```

For endpoint behavior changes, add or manually verify:

- Fixed category success and invalid category failure.
- Extra-field rejection.
- Missing-key `503` without secret leakage.
- Rate-limit `429` at configured minute/hour ceilings.
- Provider parsing success for exactly-six output and controlled failure for invalid output.
- Secret scan before public commit: no real `.env`, provider key, token, or password.

### 7. Wrong vs Correct

#### Wrong

```python
class GenerateOptionsRequest(BaseModel):
    prompt: str

# Browser/user controls arbitrary prompts and the server forwards them to the AI.
```

#### Correct

```python
Category = Literal["food", "play", "movie"]

class GenerateOptionsRequest(BaseModel):
    category: Category
    model_config = {"extra": "forbid"}

# Server owns the prompts and maps only fixed categories to provider calls.
```

---

## Required Patterns

- Use Pydantic models for public API request/response bodies.
- Keep provider keys in server-side environment variables only.
- Public AI endpoints must define fixed-scope inputs and reject extra fields.
- No-login AI endpoints must include per-IP rate limiting and a small request-size ceiling.
- Keep provider prompt construction server-side in `dashscope_client.py`.
- Normalize and validate provider output before returning it to the frontend.
- Docker/README examples must use placeholders only; never include real credentials.
- Prefer small pure helpers for reusable logic (`_read_int`, `normalize_options`, `parse_options`, `RateLimiter.allow`).

---

## Forbidden Patterns

- Do not put provider keys in frontend build variables or source files.
- Do not let unauthenticated users send arbitrary prompts to a paid AI provider unless product requirements explicitly accept that risk.
- Do not silently substitute fixed fallback AI content when a provider response violates the response contract; return a controlled error so failures are visible.
- Do not introduce a database, queue, cache service, auth system, or logging stack for the current scope without a separate design task.
- Do not return raw provider payloads, stack traces, or secret-bearing values to clients.

---

## Code Review Checklist

- [ ] Provider key is read only by backend settings/config/provider code.
- [ ] Request schema rejects unknown fields.
- [ ] The frontend cannot influence provider prompt text beyond documented enum-like inputs.
- [ ] Rate-limit behavior remains active for public AI generation.
- [ ] Request-size middleware still protects write requests.
- [ ] Provider output is checked for exactly six options before returning.
- [ ] Public docs and examples contain no real secrets.
- [ ] New modules keep the current flat structure unless duplication justifies a layer.
