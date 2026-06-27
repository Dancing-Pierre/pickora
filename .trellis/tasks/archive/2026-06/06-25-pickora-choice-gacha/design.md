# Design: Pickora choice gacha site

## Architecture

Pickora will be a single-repository web application with two runtime services:

1. **Frontend**: Vue 3 + Vite + TypeScript single-page application.
2. **API proxy**: Minimal Python FastAPI service that exposes a small AI option-generation endpoint and hides the DashScope API key from the browser.

A Docker Compose deployment will run:

- `frontend`: Nginx serving the built Vue app and proxying `/api/*` to the API service.
- `api`: FastAPI app for AI generation, health check, CORS, validation, and rate limiting.

The first delivery creates code and deployment files only. It does not deploy to 1Panel.

## Repository layout

Create the public project under `pickora/` so workspace scaffolding files are not pushed.

```text
pickora/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── api/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dashscope_client.py
│   │   ├── rate_limit.py
│   │   └── schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── deploy/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Frontend behavior

### Main single-page flow

1. Show Pickora brand and short value proposition.
2. Show the three AI category buttons: `吃什么`, `去哪玩`, `看什么剧/电影`.
3. Show manual option input:
   - Paste into a large textarea.
   - Add/remove individual option tags.
   - Parse separators: newline, regular comma, Chinese comma, Chinese dunhao, semicolon, spaces.
4. Validate custom options:
   - Minimum 3.
   - Maximum 12.
   - Trim whitespace.
   - Drop empty values.
   - De-duplicate exact repeated values.
5. Display options as cards.
6. Run GSAP draw animation.
7. Show result card, redraw count, and actions.
8. Save completed session to local history.
9. Show last five complete sessions and allow reusing their option lists.

### Card draw logic

- Initial draw chooses a random item from the current cards.
- Redraw limit is `max(1, floor(card_count / 3))`.
- Redraws may repeat prior results.
- Each draw increments draw count.
- Each redraw decrements remaining redraws.

### History model

Store in `localStorage` under a stable key such as `pickora:history:v1`.

Each entry:

```ts
type ChoiceSession = {
  id: string
  source: 'manual' | 'food' | 'play' | 'movie'
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
  finalResult: string
  drawCount: number
  redrawCount: number
  createdAt: string
}
```

Keep only the five newest entries.

### Footer

Footer must render:

```text
暗蚀工研科技 · 专业全栈技术服务 | © 2026 ansion.top · 保留所有权利 | 浙ICP备2025172295号-1
```

The company text links to `https://www.ansion.top/`.

## Animation design

Use GSAP for game-level card motion:

- Poker-like card backs.
- Card spread / shuffle motion before draw.
- Selected card lift, glow, rotate, and flip reveal.
- Result highlight with subtle burst/shine.
- Respect mobile-first layout and avoid animations that cause excessive layout shifts.

Implementation should keep animation orchestration isolated from business rules so random selection remains testable.

## API proxy design

### Endpoints

#### `GET /health`

Returns basic service status.

#### `POST /api/generate-options`

Request:

```json
{
  "category": "food"
}
```

Allowed categories:

- `food` -> `吃什么`
- `play` -> `去哪玩`
- `movie` -> `看什么剧/电影`

Response:

```json
{
  "category": "food",
  "options": ["黄焖鸡", "兰溪手擀面", "麻辣烫", "牛肉粉", "石锅拌饭", "烤肉拌饭"]
}
```

### Validation

- Reject categories outside `food`, `play`, `movie`.
- Reject unexpected large payloads.
- Always return exactly six normalized non-empty options when successful.
- If DashScope returns invalid output, retry parsing locally only if the response contains enough candidates; otherwise return a controlled error.

### DashScope prompt shape

The backend owns fixed prompts. The frontend cannot send arbitrary prompts.

Prompt intent:

- Generate exactly six short Chinese options.
- No explanations.
- No numbering if possible; JSON array preferred.
- Keep options realistic and everyday.

### Environment variables

```env
DASHSCOPE_API_KEY=
DASHSCOPE_MODEL=qwen-turbo
FRONTEND_ORIGIN=https://pickora.ansion.top
AI_RATE_LIMIT_PER_MINUTE=5
AI_RATE_LIMIT_PER_HOUR=30
```

No real key is committed. `.env.example` documents placeholders only.

## Abuse protection

Because the site has no login, protections are low-friction rather than absolute:

- Keep API key only in API container environment.
- Frontend never receives the API key.
- Fixed category allowlist blocks arbitrary prompt abuse.
- Per-IP in-memory rate limiting defaults to 5/minute and 30/hour.
- CORS allows configured frontend origin in production.
- API returns clear 429 errors when limited.
- Manual draw remains usable when AI is unavailable or unconfigured.

In-memory rate limiting is acceptable for the first single-instance deployment. If multiple API replicas are added later, move rate limiting to Redis or an edge layer.

## Deployment design

Docker Compose should build and run both services.

- The frontend image builds Vue assets and serves them with Nginx.
- Nginx proxies `/api/` to the FastAPI service.
- The API reads DashScope and rate-limit settings from environment variables.
- README explains how to configure 1Panel with Compose and environment values.

No direct 1Panel login or deployment is performed by the assistant.

## Security and secret handling

- Never commit `.env`.
- Never write real keys or passwords to README, examples, logs, tests, or code comments.
- Mention in README that users should rotate any previously exposed keys before deployment.
- Avoid logging request bodies or generated results unless needed for local debug.

## Trade-offs

- Minimal Python proxy adds a backend service, but is required to keep AI keys safe.
- No database keeps the first version lightweight, but history is device-local only.
- In-memory rate limiting is simple and sufficient for one container, but not distributed.
- Game-level animation improves product feel but requires careful mobile performance handling.
