# Technical Design: Simplify One-Page Card Draw UX

## Overview

This task reshapes Pickora from a long form-like page into a compact card-first experience. The main screen should prioritize: compact hero, compact AI/manual option entry, a playing-card fan, manual flip, and a small shuffle control. History becomes an overlay opened from a floating button.

The implementation should keep the current Vue 3 single-page architecture and avoid adding routing or global state. The only planned dependency addition is `lucide-vue-next` for system icons, per product preference.

---

## Files and Boundaries

### Frontend

- `pickora/frontend/package.json`
  - Add `lucide-vue-next` dependency after user confirms package installation.
- `pickora/frontend/src/types/choice.ts`
  - Adjust history/session type so recent entries represent reusable card sets, not selected results.
- `pickora/frontend/src/composables/useChoiceHistory.ts`
  - Deduplicate and persist reusable card sets.
  - Remove selected-result requirements from the persistence contract.
- `pickora/frontend/src/lib/choices.ts`
  - Reuse existing parsing/validation helpers.
  - Add small helper(s) only if needed for stable card-set IDs/signatures.
- `pickora/frontend/src/lib/api.ts`
  - Keep existing API wrapper and six-option validation.
- `pickora/frontend/src/App.vue`
  - Main state-machine change: option set → face-down fan → first card flip locks result → shuffle resets fan.
  - Collapse manual input into a drawer/overlay entry.
  - Replace bottom draw-action panel with top-right deck shuffle button.
  - Replace normal history panel with floating button and bottom drawer.
  - Use `lucide-vue-next` icons instead of emoji system icons.
- `pickora/frontend/src/style.css`
  - Compact one-screen layout.
  - Playing-card styling.
  - Single-/two-row fan layout.
  - Manual drawer and history drawer styles.

### Backend

- `pickora/api/app/dashscope_client.py`
  - Strengthen `build_prompt()` to generate more concrete, internally consistent options.
  - Preserve fixed-category contract, JSON-array-only output, and six-option parsing.

---

## UI Layout Design

### Main Screen

Recommended vertical order:

1. Compact hero row/card:
   - Smaller title: “别纠结了，抽一张。” should fit one line on common mobile widths.
   - Reduce supporting copy or make it one short line.
2. Compact option controls:
   - AI category buttons remain always visible and horizontal where practical.
   - Manual input is a compact entry button/chip; opens drawer/overlay only when needed.
3. Deck stage:
   - Primary visual focus.
   - Includes top-right `↻ 洗牌` control using a Lucide icon plus text or accessible label.
   - Contains fan layout of cards.
4. Floating history button:
   - Fixed bottom-right; opens bottom half-screen drawer.
5. Footer remains low priority and can be visually compact.

---

## Card State Machine

### State

Use simple local refs in `App.vue`:

- `options`: current card labels.
- `currentSource`, `currentAiGenerated`: source metadata.
- `flippedIndex`: `number | null` for the selected flipped card.
- `result`: selected card label or empty string.
- `isShuffling`: disables flip/shuffle while animation runs.
- `manualDrawerOpen`: controls manual input drawer.
- `historyDrawerOpen`: controls history drawer.
- `activeSetSignature`: stable signature for current option set to avoid duplicate history entries.

### Flow

1. AI generation or manual apply calls `setOptions(nextOptions, source, aiGenerated)`.
2. `setOptions()` normalizes options, clears result/flipped state, computes/sets set signature, and saves the card set to history once.
3. Cards render face-down in fan layout.
4. User taps a card:
   - If no validation error, not shuffling, and no card has been flipped, flip only that card.
   - Set `result` to the card label.
   - Lock the round: further card taps do nothing until shuffle.
5. User taps deck `洗牌`:
   - Animate cards collecting/shuffling/resetting.
   - Clear `result` and `flippedIndex`.
   - Keep the same options and history entry.
6. User taps history entry:
   - Restore its options/source metadata.
   - Close history drawer.
   - Reset fan to face-down state.

---

## History Contract

Current `ChoiceSession` stores selected-result fields. This should become a reusable card-set shape.

Proposed type:

```ts
export type ChoiceCardSet = {
  id: string
  source: ChoiceSource
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
  createdAt: string
}
```

Compatibility handling:

- Existing localStorage entries may still contain old `ChoiceSession` fields.
- `readHistory()` can tolerate both shapes by checking `options` and source fields; extra old fields can be ignored.
- Keep the same storage key `pickora:history:v1` unless migration complexity is needed. Since old entries include `options`, they remain reusable.

Deduplication:

- Avoid adding duplicate card sets when the same option list/source is reused or reshuffled.
- A simple signature can be `source + '|' + options.join('')` after normalization.
- When adding an existing set again, move it to the top rather than duplicating it.
- Keep max 5 entries.

---

## Fan Layout Design

### Card Count Rules

- 3–7 cards: single fan.
- 8–12 cards: two-row/two-arc fan.

### Implementation Approach

Keep this data in Vue template calculations rather than introducing a layout library.

Possible helper in `App.vue`:

```ts
function getCardStyle(index: number, total: number) {
  // Return CSS custom properties for row, rotation, x/y offset, and z-index.
}
```

Cards can be absolutely positioned inside `.card-fan`, using CSS variables:

- `--card-rotate`
- `--card-x`
- `--card-y`
- `--card-z`

This avoids duplicating CSS classes per count and keeps the layout adaptive.

---

## Animation Design

Use existing GSAP dependency.

### Shuffle

- Kill existing tweens before starting new animation.
- Reset flipped card inner rotations to face-down.
- Animate cards inward with slight random x/y/rotation.
- Optionally reorder visual motion without changing the option array.
- Animate back into fan positions.

### Flip

- Flip clicked `.card-inner` by rotating Y to 180 degrees.
- Emphasize selected card with small lift/glow.
- Dim or slightly lower non-selected cards after result locks.

Keep animations short to support the one-screen quick-play feel.

---

## AI Prompt Design

`build_prompt(category)` should be category-specific instead of one generic instruction.

Food prompt rules:

- Return either 6 brand/store names OR 6 concrete dish/food names.
- Do not mix brands and dish names in one response.
- Do not return action phrases like “吃火锅” or “喝奶茶”.
- Prefer directly comparable options.
- Return JSON string array only.

Play/movie prompts should similarly prefer concrete destinations/activities/titles/categories instead of vague verbs.

The backend still:

- Accepts only fixed categories.
- Returns exactly six normalized strings.
- Does not accept arbitrary prompts from the frontend.

---

## Accessibility and Interaction Notes

- Cards should be buttons or have button semantics so they are keyboard/touch accessible.
- Each face-down card should have an accessible label like “翻开第 N 张卡”.
- The shuffle icon button needs an accessible label.
- Drawers need close controls and backdrop dismissal if simple to implement.
- Avoid emoji for system icons; use `lucide-vue-next` icons.

---

## Trade-offs

- Keeping everything in `App.vue` matches current project structure and avoids over-abstraction, but the file will remain large.
- A local fan-style helper is simpler than introducing a card-layout component hierarchy now.
- Keeping storage key `pickora:history:v1` avoids migration code, but `readHistory()` must tolerate old result-bearing entries.
- `lucide-vue-next` adds a dependency; this is explicitly preferred by the user over local SVG icons.

---

## Rollback Considerations

- Frontend changes are mostly confined to `App.vue`, `style.css`, and history type/composable files.
- Backend prompt changes are confined to `dashscope_client.py`.
- If icon dependency causes issues, replace imports with local SVG components and remove dependency.
