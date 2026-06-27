# Type Safety

> Type safety patterns in this project.

---

## Overview

The frontend uses TypeScript in strict mode with Vue SFC support. `pickora/frontend/tsconfig.json` sets `strict: true`, `allowJs: false`, `isolatedModules: true`, and `noEmit: true`. The build script runs `vue-tsc --noEmit` before Vite builds.

Keep types explicit at API/domain boundaries and let local computed values infer simple types where clear.

---

## Type Organization

Shared frontend domain and API types live in `pickora/frontend/src/types/choice.ts`:

- `ChoiceSource`: all possible option sources, including `manual`.
- `ChoiceCardSet`: complete persisted reusable card-set shape for local history.
- `AiCategory`: excludes `manual` from `ChoiceSource` for AI-only calls.
- `AiOptionResponse`: expected backend response shape for generated options.
- `ApiErrorResponse`: tolerated backend error body shape.

Use type-only imports for shared types:

```ts
import type { AiCategory, ChoiceCardSet, ChoiceSource } from './types/choice'
```

Keep function signatures explicit when they form a reusable contract:

- `generateOptions(category: AiCategory): Promise<AiOptionResponse>` in `src/lib/api.ts`.
- `normalizeOptions(values: string[]): string[]` in `src/lib/choices.ts`.
- `validateOptionCount(options: string[]): string | null` in `src/lib/choices.ts`.

---

## Validation

There is no frontend runtime validation library such as Zod or Yup. Use focused runtime checks at external or untrusted boundaries:

- API response boundary: `src/lib/api.ts` checks `Array.isArray(data.options)` and requires exactly six options before returning.
- localStorage boundary: `src/composables/useChoiceHistory.ts` catches JSON parse errors and accepts only arrays.
- User input boundary: `src/lib/choices.ts` normalizes option strings and validates the 3-to-12 option count.

Backend schema validation remains the source of truth for accepted AI categories and extra-field rejection.

---

## Common Patterns

- Use union types for fixed product categories:

```ts
export type ChoiceSource = 'manual' | 'food' | 'play' | 'movie'
export type AiCategory = Exclude<ChoiceSource, 'manual'>
```

- Use `Record` for label maps that must cover every union member:

```ts
const sourceLabels: Record<ChoiceSource, string> = {
  manual: '手动输入',
  food: '吃什么',
  play: '去哪玩',
  movie: '看什么剧/电影'
}
```

- Type DOM refs explicitly when interacting with elements:

```ts
const deckRef = ref<HTMLElement | null>(null)
```

- Prefer `unknown`-safe error handling with `instanceof Error`:

```ts
aiMessage.value = error instanceof Error ? error.message : 'AI 生成暂时失败，可以先手动输入选项。'
```

---

## Forbidden Patterns

- Do not use `any` for API responses; cast to a named boundary type and validate required fields.
- Do not loosen `tsconfig.json` strictness to make a feature compile.
- Do not duplicate category string unions in multiple files; use `ChoiceSource` and `AiCategory`.
- Do not store `Date` objects in persisted session types; use ISO strings (`createdAt: string`).
- Do not use non-null assertions on DOM refs before checking that elements exist.
- Do not accept backend option responses without checking `options.length === 6`.
