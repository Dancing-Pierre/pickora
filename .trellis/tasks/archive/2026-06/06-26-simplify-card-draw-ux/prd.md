# Simplify one-page card draw UX

## Goal

Make Pickora feel like a compact one-screen card-drawing experience instead of a long scrolling form. Reduce vertical space, make the cards look more like real playing cards, switch the draw interaction from button-driven random draw to manual card flipping, improve AI option specificity, and move history into an unobtrusive floating entry.

## User Value

- Users should understand and play immediately without scrolling through multiple panels.
- The main visual focus should be the card fan and manual flip interaction.
- AI-generated options should feel directly usable and concrete, not generic actions.
- Recent sessions should remain available without occupying page height.

## Confirmed Facts From Repository

- Frontend is a Vue 3 + Vite + TypeScript single-page app.
- Main UI and interaction logic currently live in `pickora/frontend/src/App.vue`.
- Global styles and responsive layout currently live in `pickora/frontend/src/style.css`.
- Frontend helpers exist in:
  - `pickora/frontend/src/lib/choices.ts` for parsing, validation, redraw limit, and random picking.
  - `pickora/frontend/src/lib/api.ts` for `/api/generate-options` calls and response validation.
  - `pickora/frontend/src/composables/useChoiceHistory.ts` for localStorage history.
  - `pickora/frontend/src/types/choice.ts` for shared types.
- Current hero title is large (`h1` uses `clamp(42px, 12vw, 72px)`) and can wrap.
- AI category buttons are already three-column on wider screens, but collapse to one column under 520px.
- Current draw UX uses bottom buttons: `开始抽卡` / `重抽一次`.
- Current draw logic picks a random option, flips/highlights the chosen card, and immediately writes a history session on every draw/redraw.
- Current card layout is a grid, not a fan.
- Current card size is relatively wide/short (`choice-card` minimum height 132px with grid columns).
- Current history panel occupies normal document flow near the bottom.
- Backend AI prompt is built in `pickora/api/app/dashscope_client.py`; current prompt asks for 6 short Chinese options but does not strongly forbid generic verbs such as “吃火锅 / 喝奶茶”.

## Requirements

### Layout / Visual Density

- Compress the homepage toward a one-screen experience, especially on mobile.
- Reduce hero size so “别纠结了，抽一张。” stays smaller and preferably on one line.
- Keep AI category actions compact and horizontally arranged where screen width allows, including mobile if feasible.
- Reduce vertical spacing between hero, AI controls, manual input controls, and deck.

### AI Generation

- Improve backend prompt so generated options are concrete choices, not generic action phrases.
- Food AI options should be internally consistent for easier comparison: either a full set of restaurant/brand/store names, or a full set of concrete food/dish names. Do not mix brands and food names in the same generated set.
- Food AI options should avoid action phrases like “吃火锅” / “喝奶茶”; use nouns such as “海底捞” or “黄焖鸡”.
- Keep existing backend safety contract: fixed categories only, six options, JSON array only, no arbitrary frontend prompt.

### Card Interaction

- Replace button-driven draw with manual card flipping.
- Cards should look more like playing cards: taller, narrower, more elegant.
- Cards should fan out instead of appearing as a grid.
- Fan layout should adapt to card count: 3–7 cards use a single fan; 8–12 cards use a two-row/two-arc fan so each card remains tappable on mobile.
- User clicks a face-down card to reveal the result.
- After the first card is flipped, the round locks to that single result; other cards cannot be flipped until the user shuffles again.
- Remove the bottom `开始抽卡` / `重抽一次` button panel to save space.
- A compact `↻ 洗牌` control should live in the deck area's top-right corner when cards exist.
- A redraw/retry should shuffle or reset the fan with a visible animation, then let the user flip again.

### History

- History should use a bottom-right floating button and open a bottom half-screen drawer.
- The UI should not use emoji as system icons; use Vue/SVG icon components instead.
- History should record reusable card sets/options only, not the selected result.
- A card set should be saved once when options are created or loaded for play; subsequent flips or shuffles of the same set should not create duplicate history entries.

### Existing Behavior To Preserve

- Manual input should default to a compact collapsed entry and expand only when needed, preferably as a drawer or overlay so the main deck remains the visual focus.
- AI generation still supports `food`, `play`, and `movie` categories.
- Manual option validation remains 3 to 12 options.
- Recent history remains capped to 5 complete sessions in localStorage.
- Frontend must still build with `npm run build`.
- Backend must still compile with `python -m compileall app`.

## Acceptance Criteria

- [ ] Page is visually compressed so the core play flow is usable with much less vertical scrolling than the current version.
- [ ] Hero title is smaller and does not wrap under normal mobile widths targeted by the app.
- [ ] AI category controls are compact and horizontally arranged when practical.
- [ ] Backend AI prompt produces more concrete candidate options and explicitly discourages generic action phrases.
- [ ] Deck uses tall/narrow playing-card styling.
- [ ] Cards display in a fan layout instead of a grid.
- [ ] User can flip a card manually by clicking/tapping it.
- [ ] Bottom draw-action panel is removed.
- [ ] Redraw/reset has a shuffle/reset animation and returns cards to a flippable state.
- [ ] History is opened from a floating entry and no longer consumes normal page height.
- [ ] History entries save reusable card sets/options only and do not need to store the selected result.
- [ ] Reusing a history entry restores its option set and source metadata.
- [ ] `cd pickora/frontend && npm run build` passes.
- [ ] `cd pickora/api && python -m compileall app` passes.

## Out of Scope

- Adding login, accounts, database persistence, or cross-device sync.
- Adding arbitrary user prompts to the AI endpoint.
- Adding a new frontend framework, router, or global state library.
- Changing deployment topology.

## Open Questions

None blocking. Planning is ready for review.
