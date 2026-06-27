# Movie DB draw and drink AI category

## Goal

Update Pickora so the “看什么” category no longer uses AI generation. It should draw candidate movies from the existing `maoyan_film` table populated by the spider project. Also add a new “喝什么” category that continues to use AI generation, with concrete drink/shop suggestions such as 一点点、沪上阿姨、东方墨阑.

## User Value

- Users get movie choices from fresh spider-collected cinema data instead of generic AI suggestions.
- The app gains a practical drink decision category while preserving the compact card-draw UX.
- Backend keeps provider keys and database access server-side only.

## Confirmed Facts From Repository

- Current Pickora backend is a small FastAPI proxy under `pickora/api/`.
- Current AI endpoint is `POST /api/generate-options` in `pickora/api/app/main.py`.
- Backend request category allowlist currently lives in `pickora/api/app/schemas.py` as `Literal["food", "play", "movie"]`.
- AI prompt construction lives in `pickora/api/app/dashscope_client.py`.
- Frontend category types live in `pickora/frontend/src/types/choice.ts`.
- Frontend API wrapper validates `/api/generate-options` responses in `pickora/frontend/src/lib/api.ts`.
- Main UI category buttons and local draw state live in `pickora/frontend/src/App.vue`.
- `maoyan_film.sql` exists at project root and `spider/file/maoyan_film.sql`.
- Root `maoyan_film.sql` export shows MySQL table `maoyan_film` in database `company_website` with fields including `id`, `movieid`, `name`, `detail_url`, `poster`, `type`, `actors`, `release_date`, `score`, `ticket_buy`, `state`, and timestamps.
- Spider code `spider/volumes/app/maoyan_spider/maoyan_spider.py` writes/upserts to `maoyan_film` and marks currently active rows with `state = 1`.
- Spider DB config is loaded from `spider/volumes/config.ini` via `spider/volumes/app/common/config.py` and `common.get_mysql_conn()`. The config file may contain secrets and should not be copied into source or displayed.
- User clarified that the production table already exists on the server DB; the SQL export is only for local reference because the AI cannot access the intranet DB.
- User clarified that “看什么” must draw only rows where `maoyan_film.state = 1`; if fewer than six usable active rows exist, the backend should return a controlled failure rather than falling back to all rows.
- User clarified that “喝什么” should continue to use AI.
- Current backend dependencies are `fastapi`, `uvicorn[standard]`, `httpx`, and `pydantic`; no MySQL client dependency is currently present in Pickora API.
- Current Pickora deployment files include a root `pickora/docker-compose.yml` with separate `api` and `frontend` services; `pickora/api/Dockerfile` builds the FastAPI service, and `pickora/frontend/Dockerfile` builds the frontend nginx image.
- User clarified that API deployment should be API-owned only: the backend should run its own exposed container, root `pickora/docker-compose.yml` can be removed, and domain reverse proxy is handled externally by the user.
- User clarified that this task should not manage or depend on `pickora/deploy/nginx.conf`.
- User clarified that API deployment must use the same Docker network shape as the spider service, including external `1panel-network`, otherwise API-to-MySQL communication can fail.
- User clarified that movie table fields beyond `name` can be used, including poster and other metadata, if useful for the card experience.

## Requirements

### Movie / “看什么” Data Source

- “看什么” must stop using DashScope AI.
- “看什么” should retrieve movie options from backend-side database access to the existing `maoyan_film` table.
- The backend should use the SQL export only as a schema/reference for development, not as the runtime data source.
- Runtime database credentials/configuration must be provided through environment variables or an equivalent deployment-safe configuration path; secrets must not be committed.
- API deployment should be self-contained under `pickora/api/`: provide a backend container entrypoint/compose shape that exposes the FastAPI port directly.
- Remove root `pickora/docker-compose.yml`; root-level frontend/API orchestration is out of scope for this app going forward.
- Do not manage external domain reverse proxy or nginx config in this task.
- Movie candidates must come from usable `maoyan_film.name` values where `state = 1`.
- Do not fall back to inactive/all rows when fewer than six active rows exist; fail with a controlled Chinese error instead.
- The movie draw experience should use additional table metadata such as `poster`, `type`, `score`, `release_date`, and `detail_url` without making movie cards visually larger or awkward compared with food/drink cards.
- Movie cards should keep the same card footprint as other categories.
- After a movie card is flipped, its front face can use the poster as a background image with a readable overlay for the movie name.
- Long movie names should be handled with line clamp / smaller text / gradient overlay rather than resizing the card.
- A second click/tap on a flipped movie card, or a compact detail affordance, should open a modal/drawer with richer movie details such as poster, type, score, actors, release date, and detail link.
- If there are fewer than six usable movie rows or DB access fails, return a controlled Chinese error and keep manual input usable.

### Drink / “喝什么” AI Category

- Add a new `drink` / “喝什么” category to the fixed category allowlist.
- “喝什么” should continue through the AI generation path.
- Drink AI prompt should generate concrete beverage brands only, not vague actions or drink categories.
- Use a fixed brand allowlist / brand-like candidate style such as 古茗、沪上阿姨、瑞幸、喜茶、奈雪的茶、蜜雪冰城、茶百道、一点点、霸王茶姬、茶颜悦色.
- Keep fixed-category API safety: no arbitrary frontend prompt.

### Frontend

- Add a compact “喝什么” category button to the existing quick action area.
- Keep compact one-screen UX and card fan interaction unchanged.
- “看什么” should still appear as a category button, but its backend path should be DB-backed instead of AI-backed.
- History should continue to store reusable card sets only.
- Labels and messages should remain Chinese and understandable when movie DB generation fails.

### Backend / API

- Preserve the public response shape `{ category, options }` unless design shows a clear need to split endpoints.
- Preserve rate limiting for generation endpoints.
- Do not expose database errors, credentials, stack traces, or provider payloads to the frontend.
- Do not add user-controlled SQL filters or arbitrary prompts.

## Acceptance Criteria

- [ ] “看什么” button returns six movie names from `maoyan_film` instead of calling DashScope AI.
- [ ] Movie selection uses only `state = 1` rows and ignores blank names.
- [ ] Movie DB failures produce a controlled Chinese error without leaking DB internals.
- [ ] “喝什么” button exists in the frontend and returns six AI-generated drink/shop options.
- [ ] Backend category allowlist includes `drink` while preserving fixed-category validation and extra-field rejection.
- [ ] Existing `food` and `play` AI categories continue to work.
- [ ] Movie cards keep the same card footprint as food/drink cards, so the fan layout does not look visually broken.
- [ ] Flipped movie cards can use poster imagery as the card-front background with readable title overlay.
- [ ] Long movie names remain readable through line clamp, smaller text, or gradient overlay without resizing the card.
- [ ] Tapping/clicking a flipped movie card opens a modal/drawer with richer movie details when metadata is available.
- [ ] API can be run as its own backend container with an exposed FastAPI port and required env vars.
- [ ] Root `pickora/docker-compose.yml` is removed or no longer used for frontend/API orchestration.
- [ ] `cd pickora/frontend && npm run build` passes.
- [ ] `cd pickora/api && python -m compileall app` passes.

## Out of Scope

- Building or modifying the spider crawler itself.
- Running the intranet production database from this environment.
- Adding arbitrary movie filters/search in the frontend.
- Adding login/accounts or user-specific preferences.
- Adding a full ORM/migration framework unless required by implementation constraints.

## Open Questions

None blocking. Planning is ready for implementation.
