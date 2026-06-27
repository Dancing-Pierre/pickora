# State Management

> How state is managed in this project.

---

## Overview

Pickora uses Vue local state plus one browser-local composable. There is no Pinia, Vuex, router state, backend session, or database-backed user state.

State should stay close to the feature that owns it:

- Current screen interaction state lives in `pickora/frontend/src/App.vue` as `ref()` and `computed()` values.
- Browser-persistent recent card sets live in `pickora/frontend/src/composables/useChoiceHistory.ts`.
- Pure domain rules live in `pickora/frontend/src/lib/choices.ts`.
- AI response data is fetched on demand through `pickora/frontend/src/lib/api.ts` and then copied into local screen state.

---

## Scenario: Browser-Local Reusable Card Sets

### 1. Scope / Trigger

- Trigger: A no-login app needs lightweight recent history for reusing option sets, without accounts, database storage, selected-result logs, or cross-device sync.
- Applies to frontend-only persistence where data is user-local, non-critical, and used to replay a card set.

### 2. Signatures

```ts
type ChoiceCardSet = {
  id: string
  source: 'manual' | 'food' | 'play' | 'movie'
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
  createdAt: string
}

function createCardSetSignature(source: ChoiceSource, options: string[]): string

function useChoiceHistory(): {
  history: Ref<ChoiceCardSet[]>
  addCardSet(cardSet: Omit<ChoiceCardSet, 'id' | 'createdAt'>): void
  clearHistory(): void
}
```

### 3. Contracts

- Storage key format is versioned: `pickora:history:v1`.
- Store reusable card sets/options only; do not store the selected result as part of the current contract.
- Required persisted fields:
  - `id`: stable entry identifier.
  - `source`: `manual`, `food`, `play`, or `movie`.
  - `sourceLabel`: display label for the source.
  - `options`: complete reusable card labels.
  - `aiGenerated`: whether the set came from AI.
  - `createdAt`: ISO string for serialization stability.
- Keep the five newest entries.
- History is device-local and may be cleared by the browser.
- Malformed persisted data must not break the app.
- Existing older entries may include `finalResult`, `drawCount`, or `redrawCount`; readers may ignore those extra fields as long as `options` and source metadata are usable.

### 4. Validation & Error Matrix

| Condition | Expected behavior |
| --- | --- |
| Missing storage key | Return empty history |
| Malformed JSON | Return empty history and keep app usable |
| Parsed value is not an array | Return empty history |
| Entry lacks usable `options` array | Drop that entry |
| Entry lacks source/sourceLabel | Drop that entry |
| More than max entries | Truncate to newest max entries |
| Adding an existing card-set signature | Move/update existing entry instead of duplicating |
| User clears history | Remove storage key and reset reactive state |

### 5. Good/Base/Bad Cases

- Good: After AI generation or manual apply, save the complete card set once, then reuse its `options` later for another draw.
- Base: First-time visitor sees empty history and can still generate or manually create cards.
- Bad: Saving `finalResult` as the main history value turns history into a result log and prevents easy card-set reuse.
- Bad: Adding a new history entry on every flip or shuffle creates duplicates of the same card set.

### 6. Tests Required

There is no committed frontend test suite yet. For current changes, at minimum run:

```bash
cd pickora/frontend
npm run build
```

For state behavior changes, add or manually verify:

- Absent, malformed, and valid localStorage payloads.
- Legacy entries with extra result fields still load when `options` and source metadata are valid.
- Newest-first order and max-size truncation.
- Duplicate option sets move/update one existing entry rather than creating duplicates.
- Reuse flow restores prior `options`, `source`, and `aiGenerated` values.
- Clear-history updates both reactive state and localStorage.
- Flipping or shuffling a card set does not create additional history entries.

### 7. Wrong vs Correct

#### Wrong

```ts
addSession({
  options,
  finalResult,
  drawCount,
  redrawCount,
  createdAt: new Date().toISOString()
})
```

This makes history a result log and encourages duplicate entries per draw/redraw.

#### Correct

```ts
addCardSet({
  source,
  sourceLabel,
  options: [...options],
  aiGenerated
})
```

The history entry represents the reusable card set. A later flip can choose a result without changing the history contract.

---

## Card Draw State Categories

- **Local component state**: transient inputs, drawer visibility, animation flags, current result, flipped card index, current source, and AI status messages in `App.vue`.
- **Derived state**: validation errors, deck title, deck hint, result message, and fan row mode in `computed()` values.
- **Browser-persistent state**: small bounded card-set history stored in `localStorage` through `useChoiceHistory()`.
- **Server state**: AI-generated option responses; do not persist as global state unless saved as a reusable card set.

---

## Common Mistakes

- Silently truncating user-entered options before validation hides the `max options` error. Validate the full normalized list, then block drawing if it exceeds the limit.
- Letting UI components parse unknown persisted payloads directly duplicates the storage contract. Keep localStorage parsing in one composable/helper.
- Introducing Pinia/Vuex for the current single-screen app adds unnecessary global state.
- Storing AI loading/error state globally is unnecessary; `isGenerating`, `aiMessage`, and `aiMessageType` are screen-local.
- Saving history on every flip or shuffle duplicates the same card set. Save/update only the reusable option set.
