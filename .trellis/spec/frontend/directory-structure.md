# Directory Structure

> How frontend code is organized in this project.

---

## Overview

The frontend is a Vue 3 + Vite + TypeScript single-page app under `pickora/frontend/`. The current app is intentionally compact: one top-level Vue component owns the screen flow, while reusable non-UI logic lives in `src/lib/`, `src/composables/`, and `src/types/`.

Do not introduce route folders, global stores, or component libraries until the UI actually has multiple pages or repeated components.

---

## Directory Layout

```text
pickora/frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.ts                         # Vue app bootstrap
    ├── App.vue                         # Single-page UI, interactions, animation orchestration
    ├── style.css                       # Global responsive visual design
    ├── vite-env.d.ts                   # Vite/Vue ambient declarations
    ├── types/
    │   └── choice.ts                   # Shared frontend domain/API types
    ├── lib/
    │   ├── api.ts                      # Fetch wrapper for backend API
    │   └── choices.ts                  # Pure choice parsing/validation/random helpers
    └── composables/
        └── useChoiceHistory.ts         # Browser-local persistent history
```

---

## Module Organization

- Keep app bootstrap minimal in `src/main.ts`.
  - Example: it imports `style.css`, creates the Vue app, and mounts `App.vue`.
- Keep screen-level template, local refs, computed state, and GSAP animation orchestration in `src/App.vue` while the app remains a single page.
- Put pure reusable logic in `src/lib/`.
  - Example: `src/lib/choices.ts` handles option splitting, deduplication, count validation, redraw limits, and random picking.
  - Example: `src/lib/api.ts` wraps `fetch('/api/generate-options')` and validates the API response shape.
- Put reusable stateful Vue logic in `src/composables/`.
  - Example: `src/composables/useChoiceHistory.ts` owns all localStorage reads/writes for recent sessions.
- Put shared TypeScript shapes in `src/types/`.
  - Example: `src/types/choice.ts` defines `ChoiceSource`, `ChoiceCardSet`, `AiCategory`, and API response/error types.
- Keep global visual styling in `src/style.css`; the current project does not use CSS modules, Tailwind, Sass, or scoped component styles.

---

## Naming Conventions

- Vue components use `PascalCase.vue` (`App.vue`).
- Composables use `useX.ts` (`useChoiceHistory.ts`).
- Pure utility modules use lowercase plural/domain names (`choices.ts`, `api.ts`).
- Shared domain types live in `types/*.ts` and use `PascalCase` exported type names.
- Reactive variables in Vue files use descriptive lower camel case (`rawOptions`, `currentSource`, `isGenerating`).
- CSS classes use kebab-case (`hero-card`, `scene-button`, `choice-card`).

---

## Examples

- `pickora/frontend/src/App.vue` is the reference for the current single-page composition pattern.
- `pickora/frontend/src/lib/choices.ts` is the reference for pure frontend domain helpers.
- `pickora/frontend/src/lib/api.ts` is the reference for API wrappers and frontend-side response validation.
- `pickora/frontend/src/composables/useChoiceHistory.ts` is the reference for localStorage-backed composable state.
- `pickora/frontend/src/style.css` is the reference for the current global CSS and mobile-first responsive behavior.

---

## Forbidden Patterns

- Do not add Vue Router for the current one-screen app.
- Do not introduce Pinia/Vuex/global stores while `useChoiceHistory()` and local refs cover the state needs.
- Do not duplicate parsing, validation, or storage logic inside components when a `lib/` helper or composable already owns it.
- Do not put API response types inline in `App.vue`; share them through `src/types/choice.ts`.
- Do not split `App.vue` into many components unless there is repeated UI or the file becomes actively hard to maintain.
