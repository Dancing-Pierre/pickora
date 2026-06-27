# Error Handling

> How errors are handled in this project.

---

## Overview

Backend error handling is designed for a public, no-login AI proxy. Errors returned to clients must be controlled, user-safe Chinese messages. Provider payloads, stack traces, keys, and raw exception details must not be exposed.

FastAPI/Pydantic handles schema validation errors automatically, while project code explicitly handles request-size, rate-limit, missing-key, provider, and provider-format failures.

---

## Error Types

The project does not define custom exception classes. Use the existing FastAPI response patterns:

- `HTTPException` for controlled API failures.
  - Example: `pickora/api/app/dashscope_client.py` raises `503` when `DASHSCOPE_API_KEY` is missing.
  - Example: `pickora/api/app/main.py` raises `429` when `RateLimiter.allow()` rejects a client IP.
- `JSONResponse` from middleware for request-body/header problems that happen before route validation.
  - Example: `pickora/api/app/main.py` returns `413` for oversized requests and `400` for invalid `Content-Length`.
- Pydantic validation errors for invalid request payloads.
  - Example: `GenerateOptionsRequest` in `pickora/api/app/schemas.py` rejects unknown categories and extra fields.

---

## Error Handling Patterns

- Validate public request shape before calling external providers.
  - `GenerateOptionsRequest` accepts only `food`, `play`, or `movie` and forbids extra fields.
- Convert provider/network failures into controlled gateway errors.
  - `httpx.HTTPStatusError` with `401` or `403` becomes `502` with a configuration message.
  - Other `httpx.HTTPError` cases become `502` with a generic temporary-unavailable message.
- Validate provider response content before returning it.
  - `parse_options()` normalizes provider content, and `generate_dashscope_options()` only returns when exactly six options are available.
- Preserve manual fallback behavior.
  - Missing AI configuration returns `503` with a message telling the user manual input still works.
- Keep request-size checks in middleware.
  - The current middleware checks `Content-Length` first and reads the body only when needed for POST/PUT/PATCH requests without a length header.

---

## API Error Responses

Use FastAPI's standard JSON `detail` field for errors:

```json
{ "detail": "AI 服务暂时不可用，可以先手动输入选项。" }
```

Current status-code contracts:

| Condition | Status | Location |
| --- | --- | --- |
| Health check | `200` | `pickora/api/app/main.py` `/health` |
| Invalid category or extra field | `422` | Pydantic validation in `pickora/api/app/schemas.py` |
| Oversized request | `413` | Request-size middleware in `pickora/api/app/main.py` |
| Invalid `Content-Length` | `400` | Request-size middleware in `pickora/api/app/main.py` |
| Rate limit exceeded | `429` | `generate_options()` in `pickora/api/app/main.py` |
| Missing DashScope key | `503` | `generate_dashscope_options()` |
| Provider auth/network/format failure | `502` | `generate_dashscope_options()` |

---

## Common Mistakes

- Do not return raw `httpx` exception messages or provider response bodies to the browser.
- Do not leak whether a real key value exists; only say configuration should be checked.
- Do not silently replace invalid provider output with hardcoded fake options. Return a controlled `502` so the failure is visible.
- Do not add a free-form `prompt` field to the public request model; that bypasses the fixed-category safety design.
- Do not let frontend code depend on English-only backend errors; current UX messages are Chinese.
