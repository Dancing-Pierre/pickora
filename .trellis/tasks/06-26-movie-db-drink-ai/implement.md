# Implementation Plan: Movie DB Draw and Drink AI Category

## Preconditions

- User has reviewed and approved PRD/design/implementation plan.
- Task status is moved to `in_progress` with `task.py start` before editing implementation files.
- No real DB credentials are committed.
- Since production DB is intranet-only, local validation focuses on build/compile and controlled failure behavior unless the user provides local DB env.

---

## Ordered Checklist

### 1. Load applicable specs

Read before implementation:

- `.trellis/spec/frontend/index.md`
- `.trellis/spec/frontend/directory-structure.md`
- `.trellis/spec/frontend/component-guidelines.md`
- `.trellis/spec/frontend/hook-guidelines.md`
- `.trellis/spec/frontend/state-management.md`
- `.trellis/spec/frontend/type-safety.md`
- `.trellis/spec/frontend/quality-guidelines.md`
- `.trellis/spec/backend/index.md`
- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/error-handling.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/guides/cross-layer-thinking-guide.md`

### 2. Backend schema and config

Files:

- `pickora/api/app/schemas.py`
- `pickora/api/app/config.py`
- `pickora/api/requirements.txt`

Tasks:

- Add `drink` to public category allowlist.
- Add response metadata model for movie items and optional `items` field.
- Define AI-backed category type/guard or equivalent so `movie` cannot be passed to DashScope prompt builder.
- Add MySQL env settings with safe defaults/placeholders:
  - `MYSQL_HOST`
  - `MYSQL_PORT`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - `MYSQL_DATABASE`
  - `MYSQL_CONNECT_TIMEOUT`
- Add `pymysql` dependency.

### 3. Movie repository

File:

- `pickora/api/app/movie_repository.py` (new)

Tasks:

- Create small pure-ish helper to query six active movies from `maoyan_film`.
- Use only `state = 1` and nonblank names.
- Return normalized movie metadata aligned with option labels.
- Convert missing DB config, DB failure, invalid row count into controlled Chinese `HTTPException`.
- Do not log or return secrets / raw SQL errors.

### 4. Backend routing and prompts

Files:

- `pickora/api/app/main.py`
- `pickora/api/app/dashscope_client.py`

Tasks:

- Preserve `POST /api/generate-options`.
- Dispatch `movie` to movie repository.
- Dispatch `food`, `play`, `drink` to DashScope.
- Add `drink` prompt rules:
  - return concrete beverage brands only;
  - prefer a stable allowlist/brand-only style;
  - avoid “喝奶茶” style action phrases;
  - examples like 古茗、沪上阿姨、瑞幸、喜茶、奈雪的茶、蜜雪冰城、茶百道、一点点、霸王茶姬、茶颜悦色 are acceptable.

### 5. Frontend types and API wrapper

Files:

- `pickora/frontend/src/types/choice.ts`
- `pickora/frontend/src/lib/api.ts`
- `pickora/frontend/src/composables/useChoiceHistory.ts`

Tasks:

- Add `drink` to `ChoiceSource`.
- Add generated category type covering `food`, `play`, `movie`, `drink`.
- Add movie metadata item type.
- Allow optional `items` in API response and card-set history.
- Defensively validate `items` array shape enough to avoid runtime errors.
- Keep history dedup by source/options, not metadata.

### 6. Frontend App state and flow

File:

- `pickora/frontend/src/App.vue`

Tasks:

- Add `喝什么` scene button.
- Update `看什么` label/source metadata as needed.
- Store optional current `optionItems` from API response.
- Save card-set history with optional metadata.
- Restore metadata when reusing history.
- Update flip handler:
  - first click flips and locks as today;
  - second click on already flipped selected movie card opens details.
- Add movie detail drawer state and markup.
- Keep all non-movie categories unchanged.

### 7. Frontend styles

File:

- `pickora/frontend/src/style.css`

Tasks:

- Add poster-backed card front styles using CSS variables or inline background style.
- Add readable gradient overlay.
- Clamp long movie names without resizing cards.
- Add movie detail drawer styles following existing bottom drawer patterns.
- Ensure card fan footprint stays unchanged.

### 8. API-only Docker deployment

Files:

- `pickora/docker-compose.yml`
- `pickora/api/docker-compose.yml` (new)
- `pickora/.env.example`

Tasks:

- Remove root `pickora/docker-compose.yml`.
- Add API-local compose file that builds `api/Dockerfile` or current directory appropriately and exposes port 8000.
- Pass DashScope and MySQL env vars through the API service.
- Update `.env.example` with placeholder MySQL env vars.
- Do not touch external reverse proxy configuration.
- Do not introduce frontend Docker orchestration.

### 9. Validate

Run:

```bash
cd pickora/frontend
npm run build
```

```bash
cd pickora/api
python -m compileall app
```

If dependencies changed and lockfiles are relevant, ensure install/build path is consistent:

```bash
cd pickora/api
python -m pip install -r requirements.txt
```

Manual/code behavior checks:

- `food` and `play` still map to AI prompts.
- `drink` maps to AI prompt and frontend button.
- `movie` does not call DashScope.
- `movie` query uses only `state = 1` and nonblank names.
- Missing DB env produces controlled Chinese error.
- Movie response includes six `options`; metadata items do not break text-only categories.
- Movie cards stay same size and detail drawer opens only after a movie result is flipped.
- History restore preserves movie metadata.

---

## Risky Files / Rollback Points

- `schemas.py`: public API category and response contract. Keep backward compatible by making `items` optional.
- `main.py`: category dispatch. Ensure `movie` never reaches DashScope prompt builder.
- `movie_repository.py`: DB boundary. Keep all errors controlled and secrets out.
- `App.vue`: card interaction state. Keep first-click flip behavior unchanged.
- `useChoiceHistory.ts`: localStorage compatibility. Tolerate old entries without `items`.
- `pickora/docker-compose.yml`: deletion is intentional per user preference but affects deployment habits.

---

## Completion Criteria

- PRD acceptance criteria satisfied.
- Build/compile commands pass.
- Trellis check phase completed.
- If DB/API contracts become durable conventions, update `.trellis/spec/backend` and/or `.trellis/spec/frontend` before finish.
