# Logging Guidelines

> How logging is done in this project.

---

## Overview

The current backend does not define project-level structured logging. There are no `logging`, `structlog`, or custom logger calls in `pickora/api/app/`. Runtime logs currently come from Uvicorn/FastAPI and container output.

Because the API handles provider credentials and public requests, logging must stay conservative until a concrete observability requirement exists.

---

## Log Levels

No project-specific log-level convention exists yet. If logging is added, follow this minimal mapping:

- `info`: application lifecycle or coarse operational events that contain no user input or secrets.
- `warning`: controlled recoverable failures such as provider unavailability or malformed upstream output, without payload bodies.
- `error`: unexpected server-side failures that require operator attention, without stack traces in client responses.
- `debug`: local-only diagnostics; do not enable in production Compose defaults.

Do not add verbose request/response logging to the public AI endpoint by default.

---

## Structured Logging

There is no structured logging schema in the current codebase.

If a future task introduces logging, prefer small structured fields over interpolated blobs:

```python
# Preferred shape if logging is introduced later:
logger.warning("dashscope_request_failed", extra={"status_code": status_code})
```

Avoid logging raw request bodies, provider responses, generated options, authorization headers, or environment variables.

---

## What to Log

Current code does not log these events. If logging is introduced, these are safe candidates when sanitized:

- API startup/config source at a coarse level, without values of secrets.
- Provider request failure category and HTTP status code, not provider body.
- Rate-limit rejections as counts or event names, not full client identifiers unless a privacy policy requires it.
- Request-size rejection status, not body content.

---

## What NOT to Log

Never log:

- `DASHSCOPE_API_KEY` or any Authorization header.
- `.env` content or environment dumps.
- Raw provider request/response payloads.
- Browser-submitted option text or generated options unless a product/privacy decision explicitly allows it.
- Full IP addresses in long-lived application logs without a stated privacy/retention requirement.

---

## Current References

- `pickora/api/app/config.py` reads environment variables but does not log them.
- `pickora/api/app/dashscope_client.py` catches provider errors and returns controlled `HTTPException` details without logging payloads.
- `pickora/docker-compose.yml` uses normal container stdout/stderr behavior and does not configure an application logger.
