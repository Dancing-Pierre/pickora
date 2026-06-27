# Technical Design: Movie DB Draw and Drink AI Category

## Overview

This task changes Pickora's generated option sources while preserving the compact card draw interaction:

- `movie` / “看什么” becomes a database-backed category that reads six active movie records from `maoyan_film`.
- `drink` / “喝什么” is added as a new AI-backed category.
- Food/play/drink continue through DashScope prompts.
- Drink prompts should prefer concrete beverage brands only; avoid generic action phrases or broad drink categories.
- Movie cards may render poster-backed fronts and open a detail drawer after the card has been flipped.
- API deployment becomes API-owned only: remove root `pickora/docker-compose.yml` and provide an API-local container run/compose path.

The design keeps KISS/YAGNI boundaries: no ORM, no crawler changes, no user filters, no global frontend state, no frontend DB credentials.

---

## Architecture and Boundaries

### Backend

Files likely affected:

- `pickora/api/requirements.txt`
  - Add a MySQL client dependency.
  - Prefer `pymysql` because the existing spider project already uses it and the query is simple.
- `pickora/api/app/config.py`
  - Add environment-backed MySQL settings:
    - `MYSQL_HOST`
    - `MYSQL_PORT`
    - `MYSQL_USER`
    - `MYSQL_PASSWORD`
    - `MYSQL_DATABASE`
    - optional `MYSQL_CONNECT_TIMEOUT`
- `pickora/api/app/schemas.py`
  - Extend category allowlist with `drink`.
  - Keep `movie` as a valid public category but no longer AI-backed internally.
  - Add optional movie item response shape.
- `pickora/api/app/movie_repository.py` (new)
  - Own DB connection and movie query.
  - Normalize DB rows into typed response items.
  - Convert DB failures into controlled `HTTPException` errors.
- `pickora/api/app/dashscope_client.py`
  - Treat only AI-backed categories (`food`, `play`, `drink`) as prompt inputs.
  - Add `drink` prompt rules with a fixed brand allowlist / brand-only style.
- `pickora/api/app/main.py`
  - Keep `POST /api/generate-options` as the public endpoint.
  - Preserve rate limiting for all generated option requests.
  - Dispatch:
    - `movie` → `get_random_active_movies(settings)`
    - `food/play/drink` → `generate_dashscope_options(category, settings)`

### Frontend

Files likely affected:

- `pickora/frontend/src/types/choice.ts`
  - Add `drink` to `ChoiceSource`.
  - Split generated category types if needed:
    - `GeneratedCategory = Exclude<ChoiceSource, 'manual'>`
    - `AiCategory = Exclude<GeneratedCategory, 'movie'>`
  - Add `MovieOptionItem` and optional `items` on generated response.
  - Extend `ChoiceCardSet` with optional metadata items so history can restore movie details.
- `pickora/frontend/src/lib/api.ts`
  - Accept generated categories including `movie` and `drink`.
  - Validate `options.length === 6` for every generated category.
  - If `items` is present, validate it as an array defensively enough for UI usage.
- `pickora/frontend/src/composables/useChoiceHistory.ts`
  - Persist optional movie metadata in card sets.
  - Deduplicate by source + options as before; metadata should not create duplicate entries.
  - Tolerate old entries without metadata.
- `pickora/frontend/src/App.vue`
  - Add “喝什么” scene.
  - Keep “看什么” scene but treat returned metadata as current card item metadata.
  - Keep cards same size for all categories.
  - On first click: flip and lock as today.
  - On second click of already flipped movie card: open movie detail drawer/modal.
  - Save history with metadata so reused movie sets retain poster/details.
- `pickora/frontend/src/style.css`
  - Add poster-backed card-front styles and readable overlay.
  - Add line-clamped movie title style.
  - Add movie detail drawer/modal styles.
  - Do not resize movie cards relative to food/drink cards.

### Deployment

Files likely affected:

- `pickora/docker-compose.yml`
  - Remove root app-level compose file per user preference.
- `pickora/api/docker-compose.yml` (new)
  - API-only container deployment.
  - Expose FastAPI port directly.
  - Attach to the same external Docker network as spider: `1panel-network`.
  - Include `extra_hosts: host.docker.internal:host-gateway` to match spider's host access pattern.
  - Pass DashScope and MySQL env vars to backend.
- `pickora/api/Dockerfile`
  - Keep as backend image definition.
  - No frontend/nginx responsibility.
- `pickora/.env.example`
  - Add MySQL placeholders and API port guidance.
  - No real secrets.

The task does not manage domain reverse proxy or `pickora/deploy/nginx.conf`.

---

## API Contract

### Request

`POST /api/generate-options`

```json
{ "category": "movie" }
```

Allowed categories:

- `food` — AI
- `play` — AI
- `movie` — MySQL `maoyan_film`
- `drink` — AI

Extra fields remain forbidden.

### Response

Base response remains compatible:

```json
{
  "category": "movie",
  "options": ["玩具总动员5", "记忆碎片", "..."]
}
```

Movie responses may include metadata:

```json
{
  "category": "movie",
  "options": ["玩具总动员5", "记忆碎片", "..."],
  "items": [
    {
      "label": "玩具总动员5",
      "movieId": "1490532",
      "poster": "https://...",
      "type": "剧情／喜剧／动画",
      "actors": "汤姆·汉克斯／...",
      "releaseDate": "2026-06-19",
      "score": "9.6",
      "detailUrl": "https://www.maoyan.com/films/1490532"
    }
  ]
}
```

`options` is still the source of truth for card labels. `items` is optional UI metadata and should align by `label`/order with `options`.

---

## Movie Query Contract

Use only active rows:

```sql
SELECT movieid, name, detail_url, poster, type, actors, release_date, score
FROM maoyan_film
WHERE state = 1
  AND name IS NOT NULL
  AND TRIM(name) <> ''
ORDER BY RAND()
LIMIT 6;
```

Rules:

- If fewer than 6 usable rows are returned, fail with a controlled `502` or `503` style response.
- Do not fall back to inactive rows.
- Do not expose SQL errors or credentials.
- Normalize strings by trimming whitespace.
- Use parameterized SQL if any dynamic parameters are later added; current query has no user input.

`ORDER BY RAND()` is acceptable for the current spider hot/movie table size and simplest implementation. If table volume grows substantially, a future task can replace it with indexed random sampling.

---

## Frontend Data Flow

```text
Scene button click
  → generateOptions(category)
  → backend returns { category, options, items? }
  → App.vue setGeneratedOptions(response)
  → current options + optional movie metadata saved to history once
  → card fan renders same-size cards
  → first card click flips and locks result
  → if selected card has movie metadata and user clicks it again, open movie detail drawer
```

State additions in `App.vue`:

- `optionItems`: optional metadata aligned with `options`.
- `movieDetailOpen`: boolean.
- `selectedMovieItem`: derived from `flippedIndex` and `optionItems`.

History additions:

- `ChoiceCardSet.items?: MovieOptionItem[]`.
- Dedup remains based on `source + options`, not metadata, to avoid duplicates.

---

## UI Design

### Card Face

- All cards remain the same dimensions and fan layout.
- For movie items with a poster:
  - Use poster as `background-image` on card front.
  - Add dark/brand gradient overlay.
  - Show movie title on top of overlay.
  - Clamp title to 2–3 lines; reduce font size for long names if needed.
- For non-movie categories or movie rows without poster:
  - Use existing text card front style.

### Movie Detail Drawer

Open after tapping/clicking the already flipped selected movie card.

Show:

- Poster thumbnail/hero area if present.
- Movie name.
- Score if present.
- Type if present.
- Actors if present.
- Release date if present.
- Detail link if present.

Keep close button and backdrop dismissal consistent with existing drawer patterns.

---

## Error Handling

### Missing DB Config

Return controlled Chinese error, e.g.:

```json
{ "detail": "电影数据暂时不可用，可以先手动输入选项。" }
```

### DB Connection/Query Failure

Return controlled Chinese error. Do not expose host/user/db/table or exception text.

### Fewer Than Six Active Movies

Return controlled Chinese error, e.g.:

```json
{ "detail": "当前可用电影不足 6 部，可以先手动输入选项。" }
```

### AI Failures

Keep existing DashScope error handling for food/play/drink.

---

## Deployment Design

- Remove root `pickora/docker-compose.yml`.
- Add API-local compose/run support under `pickora/api/`.
- API container exposes port `8000` by default.
- External domain reverse proxy is user-managed and out of scope.
- Frontend Docker/nginx deployment is out of scope for this task.
- `.env.example` documents placeholders only.

---

## Trade-offs

- Reusing `/api/generate-options` avoids frontend endpoint branching and preserves the existing card setup flow.
- Adding optional `items` keeps backward compatibility with text-only categories.
- PyMySQL avoids heavy ORM/framework additions, but DB calls are synchronous. For this low-volume endpoint, run the query in a threadpool or keep it small; if traffic grows, move to async DB client or pooled connection in a separate task.
- `ORDER BY RAND()` is simple and adequate for the current movie table scale; optimize later only if needed.

---

## Rollback Considerations

- If DB access causes deployment issues, `movie` can temporarily return a controlled unavailable error while food/play/drink continue working.
- Because `/api/generate-options` remains the only endpoint, frontend rollback is confined to category/type and metadata rendering changes.
- Removing root compose is deployment-shape change; if needed, recover from git history, but do not reintroduce frontend orchestration without user approval.
