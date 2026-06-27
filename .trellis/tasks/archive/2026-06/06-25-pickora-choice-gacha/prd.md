# Build Pickora choice gacha site

## Goal

Build a simple public website called **Pickora** for quick choice-making in a flashy gacha/card-draw style. Users can either paste a short option list like "黄焖鸡 / 兰溪手擀面 / 肉夹馍" or pick one of a few simple categories such as "吃什么", "去哪玩", or "看什么剧/电影" and let AI generate a few options. The app should draw one result with a cool card animation and poker-like background, keep the last five choice sessions locally, and be ready for public GitHub hosting plus Docker Compose deployment instructions with AI configuration through environment variables.

## Confirmed Facts

- Product name: **Pickora**
- Public website, no login required
- Domain: `pickora.ansion.top`
- Deployment target: Ubuntu server managed by 1Panel
- First delivery should prepare Docker Compose deployment files and README instructions, but the assistant should not deploy to 1Panel
- Preferred stack: Vue frontend + minimal Python API proxy
- AI provider to support first: **阿里百炼 / DashScope**
- Visual direction: selection gacha, card-based, flashy, with poker-card style background
- Animation direction: game-level card draw animation using GSAP rather than minimal motion
- Responsive direction: mobile-first design, because users are likely to decide quickly on a phone
- The experience should feel simple, not like a chat app
- User can provide a short option list directly using either quick pasted text or individual option tags
- User-entered lists must contain at least 3 and at most 12 options
- If no list is provided, the app should support simple categories: `吃什么`, `去哪玩`, `看什么剧/电影`
- AI generation is triggered by clicking a category only; no extra preference/location input in the first version
- AI should generate exactly six options for the selected category by default, then the app draws from them
- Card draws should allow limited redraws: maximum redraw count is `max(1, floor(card_count / 3))`
- Redraws may repeat previous results
- The site should store the last five complete choice sessions locally and allow reuse
- Each history entry should include source/type, options, AI-generated flag, final result, draw/redraw count, and timestamp
- GitHub repository name: `pickora`
- The project should use the MIT License
- The assistant is authorized to use the local GitHub CLI (`gh`) to create the public GitHub repository and push code after implementation is ready
- Footer company text: `暗蚀工研科技 · 专业全栈技术服务`, linking to `https://www.ansion.top/`
- Footer copyright text: `© 2026 ansion.top · 保留所有权利`
- Footer ICP text: `浙ICP备2025172295号-1`
- AI abuse protection direction: no-login low-friction protection with server-side rate limiting, a fixed category allowlist, and default limits of 5 requests/minute plus 30 requests/hour per IP
- Sensitive credentials were exposed in chat and must not be stored in code, logs, or the repository
- First version will not include a backend admin panel, database, or user accounts

## Requirements

- No-login, instant access experience
- Single-page application experience
- Simple choice flow, not conversational AI chat
- Card-draw style result presentation
- User-entered short option list flow with pasted-text parsing and individual option tags
- AI-generated option flow for the three simple categories
- Local storage of the last five complete choice sessions
- Footer with company link, copyright, and ICP text
- Public-friendly repository structure
- Docker Compose deployment files and README instructions for self-deployment
- Environment-variable-based AI key configuration
- Minimal Python proxy to keep the AI key off the frontend
- Server-side AI abuse protection:
  - AI key only lives in server environment variables
  - API only accepts fixed categories: `food`, `play`, `movie`
  - Reject irrelevant or oversized request payloads
  - Restrict CORS to the configured frontend origin in production
  - Apply per-IP rate limiting with default values `AI_RATE_LIMIT_PER_MINUTE=5` and `AI_RATE_LIMIT_PER_HOUR=30`
- If no AI key is configured, manual draw should still work and AI generation should show a clear unavailable state
- Future ability to swap the AI key from an admin-side interface, but that is not part of the first delivery
- No backend admin panel, database, or user system in the first version

## Acceptance Criteria

- [ ] A user can open the site without signing in and use it immediately
- [ ] A user can enter a short custom option list and draw one result
- [ ] Pasted custom options are parsed from common separators such as newlines, spaces, commas, and Chinese punctuation
- [ ] A user can add/remove individual option tags
- [ ] Custom option validation requires 3 to 12 options
- [ ] A user can choose `吃什么`, `去哪玩`, or `看什么剧/电影` and get six AI-generated options before drawing
- [ ] AI generation does not expose the DashScope key to frontend code or browser traffic
- [ ] AI requests are limited to the fixed category set and protected by rate limiting
- [ ] The UI presents the experience as a stylish card/gacha draw with card backs and a polished reveal
- [ ] Redraws are limited by `max(1, floor(card_count / 3))` and may repeat prior results
- [ ] The app preserves the last five complete choice sessions locally and can reuse a prior session's options
- [ ] Footer displays `暗蚀工研科技 · 专业全栈技术服务 | © 2026 ansion.top · 保留所有权利 | 浙ICP备2025172295号-1`
- [ ] Footer company text links to `https://www.ansion.top/`
- [ ] The project is pushed to a public GitHub repository named `pickora`
- [ ] Repository includes an MIT `LICENSE` file
- [ ] Docker Compose files and README instructions are present for self-deployment on Ubuntu + 1Panel
- [ ] AI configuration is provided through environment variables, not committed secrets
- [ ] The frontend does not contain the AI key directly
- [ ] No real API keys or passwords are written into source files

## Out of Scope for First Version

- User accounts and login
- Database-backed cross-device history
- Admin panel for replacing API keys
- Full AI chat or conversational flow
- Payment, sharing, or social features
- Direct 1Panel deployment execution by the assistant
- Cloudflare Turnstile or other CAPTCHA unless abuse persists after launch

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` before `task.py start`.
