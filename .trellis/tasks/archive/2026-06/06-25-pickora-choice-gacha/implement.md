# Implementation Plan: Pickora choice gacha site

## Pre-implementation gate

- Confirm this plan with the user before starting implementation.
- Run Trellis task activation only after review approval.
- Keep all generated app code under `pickora/`; do not push `.trellis/`, `.claude/`, or private workspace files.

## Ordered checklist

### 1. Scaffold project

- Create `pickora/` directory.
- Initialize frontend with Vue 3 + Vite + TypeScript.
- Add GSAP dependency.
- Add minimal styling setup suitable for mobile-first custom UI.
- Create Python FastAPI API service structure.
- Add `.gitignore`, `.env.example`, `LICENSE`, and initial `README.md`.

### 2. Build API proxy

- Implement settings loader for:
  - `DASHSCOPE_API_KEY`
  - `DASHSCOPE_MODEL` defaulting to `qwen-turbo`
  - `FRONTEND_ORIGIN` defaulting to local development origin
  - `AI_RATE_LIMIT_PER_MINUTE=5`
  - `AI_RATE_LIMIT_PER_HOUR=30`
- Implement category allowlist: `food`, `play`, `movie`.
- Implement `/health`.
- Implement `/api/generate-options`.
- Add per-IP in-memory rate limiting.
- Add request validation and controlled error responses.
- Add DashScope client with safe fallback behavior when key is missing.
- Ensure no secret is printed or returned.

### 3. Build frontend core

- Implement option parsing utility.
- Implement session/history types.
- Implement localStorage history composable.
- Implement random draw utility and redraw limit logic.
- Implement API client for AI generation.
- Handle AI unavailable, rate-limited, and generic error states.

### 4. Build frontend UI

- Single-page mobile-first layout.
- Header/brand area.
- Three AI category buttons.
- Manual input textarea.
- Individual option tag add/remove UI.
- Card deck display.
- GSAP draw animation and result reveal.
- Redraw controls and remaining count.
- Last five history cards with reuse action.
- Required footer with company link, copyright, and ICP text.

### 5. Docker and deployment files

- Add frontend Dockerfile.
- Add API Dockerfile.
- Add Nginx config to serve frontend and proxy `/api/` to API.
- Add root `docker-compose.yml`.
- Ensure environment variables are documented and consumed correctly.

### 6. Documentation

- Write README with:
  - project overview
  - features
  - local development instructions
  - Docker Compose usage
  - 1Panel self-deployment notes
  - environment variables
  - secret handling warning and key rotation reminder
  - rate limit configuration
- Keep examples free of real secrets.

### 7. Validation

Run local checks where available:

- Frontend install/build/type-check.
- API dependency install/import check.
- API lightweight tests or manual endpoint validation.
- Docker Compose config validation.
- Secret scan by searching for known secret-like strings and ensuring `.env` is ignored.

### 8. GitHub publication

- Initialize git in `pickora/` only.
- Verify `git status` excludes workspace scaffolding and secrets.
- Commit with a conventional initial commit message.
- Use `gh` CLI to create public repository `pickora`.
- Push code to GitHub.

## Validation commands

Exact commands may be adjusted after scaffold creation, but expected checks include:

```bash
cd pickora/frontend
npm install
npm run build
```

```bash
cd pickora/api
python -m venv .venv
. .venv/Scripts/activate || . .venv/bin/activate
pip install -r requirements.txt
python -m compileall app
```

```bash
cd pickora
docker compose config
```

```bash
cd pickora
git status --short
```

## Risk points and mitigations

- **Secret leakage**: never create real `.env`; use `.env.example`; run search before commit.
- **AI abuse**: fixed categories, CORS, per-IP rate limiting, and no arbitrary prompts.
- **Mobile performance**: keep GSAP timelines scoped and avoid excessive DOM nodes.
- **No database**: history is intentionally local-only and limited to five sessions.
- **Public repo creation**: only after final file review and git status check.

## Rollback points

- If AI integration is blocked, keep manual draw working and document AI env setup.
- If GSAP animation becomes unstable, reduce timeline complexity while preserving card flip/reveal feel.
- If GitHub repo creation fails, leave local git repository ready and report the remote setup issue.
