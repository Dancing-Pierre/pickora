# Quality Guidelines

> Code quality standards for frontend development.

---

## Overview

Frontend quality for Pickora means keeping the single-page flow simple, type-safe, mobile-first, and resilient when AI generation fails. The app must remain usable with manual input even if the backend is missing a key, rate limited, or unavailable.

Current validation command:

```bash
cd pickora/frontend
npm run build
```

This runs `vue-tsc --noEmit` and then `vite build`.

---

## Forbidden Patterns

- Do not put provider keys or provider base URLs in frontend environment variables or source files.
- Do not let users send arbitrary prompts to the backend; AI generation is category-based through `AiCategory` only.
- Do not bypass `src/lib/api.ts` when calling `/api/generate-options`.
- Do not duplicate option parsing or count validation in `App.vue`; use `src/lib/choices.ts`.
- Do not call `localStorage` for history outside `useChoiceHistory()`.
- Do not add global state libraries, routing, or component frameworks for the current one-page scope.
- Do not weaken TypeScript strictness or use `any` to bypass API/localStorage uncertainty.
- Do not make the app depend on AI success; manual option entry is a required fallback.

---

## Required Patterns

- Keep API calls behind `generateOptions(category)` in `src/lib/api.ts`.
- Validate AI responses on the frontend before using them: `options` must be an array with exactly six entries.
- Keep manual choice rules centralized in `src/lib/choices.ts`:
  - split by whitespace and common Chinese/English punctuation;
  - trim and deduplicate options;
  - require 3 to 12 options;
  - compute redraw limit as `max(1, floor(cardCount / 3))`.
- Keep recent history as complete `ChoiceCardSet` objects through `useChoiceHistory()`.
  - Save/update the card set when options are created or reused.
  - Do not save selected results, flips, or shuffles as history entries.
- Use disabled button states during async or animation flows.
  - Examples: `:disabled="isGenerating || isDrawing"` for AI category buttons and draw controls in `App.vue`.
- Preserve mobile-first layout and responsive behavior in `src/style.css`.
- Use Chinese user-facing copy consistently, matching the existing product language.

---

## Testing Requirements

There is no committed unit test suite yet. For frontend changes, run:

```bash
cd pickora/frontend
npm run build
```

For behavior changes, manually verify the relevant flow in a browser:

- Manual pasted input parses by spaces, punctuation, and newlines.
- Manual validation blocks fewer than 3 and more than 12 options.
- AI category buttons call the backend, show loading text, and keep manual fallback when errors occur.
- Drawing and redraw buttons are disabled during animation.
- Redraw limit follows the current formula.
- Recent history stores complete reusable card sets, keeps five newest entries, supports reuse, deduplicates same source/options, and clears correctly.
- Mobile layout remains usable below 520px.

---

## Code Review Checklist

- [ ] New frontend code keeps business rules in `src/lib/` or `src/composables/` instead of duplicating them in the template.
- [ ] API boundary code handles non-OK responses and invalid JSON safely.
- [ ] Types come from `src/types/choice.ts` where shared across modules.
- [ ] User-facing errors remain understandable Chinese messages.
- [ ] Buttons have `type="button"` unless they intentionally submit a form.
- [ ] Async/animation flows cannot be triggered repeatedly through enabled controls.
- [ ] Styling follows existing global CSS class naming and responsive patterns.
- [ ] `npm run build` passes after changes.

---

## Current Good Examples

- `pickora/frontend/src/lib/api.ts` maps backend failures to safe messages and validates generated option count.
- `pickora/frontend/src/lib/choices.ts` centralizes option normalization and draw rules.
- `pickora/frontend/src/composables/useChoiceHistory.ts` keeps localStorage parsing and writing out of UI code.
- `pickora/frontend/src/App.vue` uses `computed()` for option errors and redraw counts instead of recalculating them in multiple handlers.
- `pickora/frontend/src/style.css` keeps the mobile layout change isolated in one media query.
