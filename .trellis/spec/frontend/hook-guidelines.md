# Hook Guidelines

> How hooks are used in this project.

---

## Overview

This Vue project uses composables for reusable stateful logic. The only current composable is `pickora/frontend/src/composables/useChoiceHistory.ts`, which owns browser-local choice history.

Use composables when logic needs Vue reactivity plus encapsulated side effects. Use `src/lib/` for pure functions that do not need `ref`, browser storage, or lifecycle behavior.

---

## Custom Hook Patterns

Project composables follow Vue naming and return plain objects:

```ts
export function useChoiceHistory() {
  const history = ref<ChoiceCardSet[]>(readHistory())

  function addCardSet(cardSet: Omit<ChoiceCardSet, 'id' | 'createdAt'>) {
    history.value = upsertNewestCardSet(cardSet, history.value).slice(0, MAX_HISTORY)
    writeHistory(history.value)
  }

  function clearHistory() {
    history.value = []
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    history,
    addCardSet,
    clearHistory
  }
}
```

Current conventions from `useChoiceHistory.ts`:

- Keep storage constants private to the module (`STORAGE_KEY`, `MAX_HISTORY`).
- Keep helper functions private unless another module needs them (`readHistory`, `writeHistory`).
- Parse unknown persisted data defensively.
- Return reactive state and mutator functions; do not expose storage implementation details to components.
- Store complete `ChoiceCardSet` objects, not selected result logs.
- Add card sets through `addCardSet()` when options are created or reused, not when a card is flipped or shuffled.

---

## Data Fetching

Data fetching is not handled by composables in the current app. It lives in `pickora/frontend/src/lib/api.ts`:

- `generateOptions(category)` posts to `/api/generate-options`.
- It maps backend errors to user-facing messages.
- It validates that `options` is an array with exactly six entries before returning data.

Keep one-off API wrappers in `src/lib/api.ts` unless multiple components need shared loading/caching state. There is no Vue Query, SWR, Pinia, or global server-state cache.

---

## Naming Conventions

- Composable files use `useX.ts` (`useChoiceHistory.ts`).
- Composable functions use the same `useX` name.
- Returned state uses noun names (`history`).
- Returned actions use imperative verbs (`addCardSet`, `clearHistory`).
- Private helpers use lower camel case (`readHistory`, `writeHistory`).

---

## Common Mistakes

- Do not let `App.vue` call `localStorage` directly for history; keep that contract in `useChoiceHistory()`.
- Do not duplicate `STORAGE_KEY` outside the composable.
- Do not throw on malformed `localStorage` JSON; return empty history and keep the app usable.
- Do not store incomplete card sets; history reuse depends on `options`, `source`, `sourceLabel`, and `aiGenerated`.
- Do not add a history entry on card flip or shuffle; those interactions only affect the current round.
- Do not create a composable for pure string parsing or random selection; those belong in `src/lib/choices.ts`.
