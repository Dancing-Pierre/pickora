# Implementation Plan: Simplify One-Page Card Draw UX

## Preconditions

- User has approved the planning artifacts.
- User has explicitly confirmed package installation for `lucide-vue-next` before running `npm install`.
- Task status is set to `in_progress` via `task.py start` before editing implementation files.

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

### 2. Add icon dependency

After explicit confirmation:

```bash
cd pickora/frontend
npm install lucide-vue-next
```

Then use named imports in `App.vue`, e.g. `History`, `Shuffle`, `X`, and a manual-entry icon if needed.

### 3. Update history data model

Files:

- `pickora/frontend/src/types/choice.ts`
- `pickora/frontend/src/composables/useChoiceHistory.ts`

Tasks:

- Replace/augment result-focused history with reusable card-set history.
- Keep source/sourceLabel/options/aiGenerated/createdAt.
- Ignore selected-result fields from old saved entries.
- Deduplicate by source + normalized options signature.
- Keep max 5 entries.
- Export `addCardSet`/`clearHistory` or keep `addSession` naming only if it remains semantically clear.

### 4. Update App state and interaction flow

File:

- `pickora/frontend/src/App.vue`

Tasks:

- Add collapsed manual drawer state.
- Add history drawer state.
- Replace draw/redraw state with:
  - `flippedIndex`
  - `result`
  - `isShuffling`
  - current card-set signature if needed
- Save history once when options are created/loaded, not when card is flipped.
- Add manual card click handler:
  - no-op if invalid, shuffling, or already flipped.
  - flip clicked card and lock result.
- Add shuffle handler:
  - reset result/flipped state.
  - play shuffle animation.
- Reuse history entries by restoring options/source and resetting fan state.

### 5. Redesign template

File:

- `pickora/frontend/src/App.vue`

Tasks:

- Compact hero.
- Compact horizontal AI category controls.
- Replace manual input panel with collapsed trigger + drawer/overlay content.
- Replace grid deck with fan deck.
- Remove bottom result/draw-action panel.
- Add top-right deck shuffle control.
- Add bottom-right history floating button and bottom drawer.
- Remove emoji system icons; use Lucide icon components.

### 6. Redesign styles

File:

- `pickora/frontend/src/style.css`

Tasks:

- Reduce vertical padding/margins.
- Make hero title smaller and one-line where practical.
- Keep AI actions horizontal on mobile unless width is too narrow.
- Create tall/narrow playing-card styling.
- Implement single fan and two-row fan using CSS variables or row classes.
- Add selected/locked/dimmed card states.
- Add manual drawer and history drawer styles.
- Add floating button styles.

### 7. Improve backend prompt

File:

- `pickora/api/app/dashscope_client.py`

Tasks:

- Make prompt category-specific.
- Food: all brand/store names OR all concrete food/dish names; no mixing; no action phrases.
- Play/movie: concrete comparable options, not vague verbs.
- Preserve JSON-array-only output and six-option contract.

### 8. Validate

Run:

```bash
cd pickora/frontend
npm run build
```

```bash
cd pickora/api
python -m compileall app
```

Manual behavior checks:

- AI category generation fills six cards.
- Manual drawer opens, parses/applies options, and closes or returns to deck.
- 3–7 cards display single fan.
- 8–12 cards display two-row fan.
- Clicking one card flips and locks result.
- Clicking other cards after result does nothing.
- `洗牌` animates reset and allows another flip.
- History floating button opens bottom drawer.
- History records reusable card sets only and does not duplicate per flip/shuffle.
- Reusing history restores card set.

---

## Risky Files / Rollback Points

- `App.vue`: largest behavior and state-machine change. Keep functions small and named clearly.
- `style.css`: many layout changes. Validate mobile width visually.
- `useChoiceHistory.ts`: ensure old localStorage entries do not break parsing.
- `package.json` / lockfile: dependency change requires user confirmation.
- `dashscope_client.py`: prompt change should not affect response parsing contract.

---

## Completion Criteria

- All PRD acceptance criteria satisfied.
- Build/compile commands pass.
- Trellis check phase completed.
- If implementation reveals reusable conventions, update `.trellis/spec/` before finish.
