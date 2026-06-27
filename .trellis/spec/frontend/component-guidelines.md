# Component Guidelines

> How components are built in this project.

---

## Overview

Pickora currently uses a single Vue SFC, `pickora/frontend/src/App.vue`, for the whole screen. This is acceptable for the current one-page product because there are no repeated component abstractions yet.

The component style is Vue 3 Composition API with `<script setup lang="ts">`, a declarative template, typed local state, and global CSS classes from `src/style.css`.

---

## Component Structure

Use the existing SFC order:

1. `<template>` first for page structure and accessibility attributes.
2. `<script setup lang="ts">` second for imports, constants, refs/computed values, and functions.
3. Styling remains in `src/style.css`, not in a component-local `<style>` block.

Current reference: `pickora/frontend/src/App.vue`.

Within `<script setup>`:

- Imports come first: Vue APIs, third-party libraries, local helpers/composables, then type-only imports.
- Constants that drive UI labels come before reactive state.
  - Example: `scenes` and `sourceLabels` in `App.vue`.
- Reactive state is declared with `ref()` and derived state with `computed()`.
- Small event handlers stay in the SFC when they are tightly coupled to the screen.
- Reusable pure logic belongs in `src/lib/`; reusable stateful logic belongs in `src/composables/`.

---

## Props Conventions

There are no child components and therefore no props in the current codebase.

If a child component is introduced later:

- Use TypeScript props via `defineProps<...>()`.
- Keep prop types narrow and import shared domain types from `src/types/choice.ts` when appropriate.
- Emit user actions instead of mutating parent state directly.
- Do not pass raw API payloads through multiple components; normalize them in `src/lib/api.ts` first.

---

## Icon Conventions

- Use `lucide-vue-next` for system icons in Vue UI.
- Import only the icons needed by the component so bundling can tree-shake unused icons.
- Do not use emoji as persistent system icons for controls such as history, shuffle, close, or manual entry.
- Decorative icons should set `aria-hidden="true"`; icon-only buttons need an `aria-label`.

Example:

```vue
<script setup lang="ts">
import { History, Shuffle, X } from 'lucide-vue-next'
</script>

<template>
  <button type="button" aria-label="打开最近卡牌">
    <History :size="22" aria-hidden="true" />
  </button>
  <button type="button" aria-label="洗牌后重新翻卡">
    <Shuffle :size="15" aria-hidden="true" />
    洗牌
  </button>
  <button type="button" aria-label="关闭">
    <X :size="18" aria-hidden="true" />
  </button>
</template>
```

---

## Styling Patterns

The project uses global CSS in `pickora/frontend/src/style.css`:

- Class names are kebab-case (`scene-button`, `option-tag`, `history-item`).
- Layout uses mobile-first constraints such as `width: min(100%, 720px)` on `.app-shell`.
- Shared visual treatment is grouped with combined selectors.
  - Example: `.hero-card, .panel, .deck-stage` share glass-card styling.
  - Example: button-like elements share cursor and transition styles.
- Responsiveness is handled with a single `@media (max-width: 520px)` block.
- There is no Tailwind, CSS module, Sass, or CSS-in-JS setup.

Keep new styles in `style.css` unless the app grows enough to justify a separate component/style architecture.

---

## Accessibility

Current accessibility patterns in `App.vue`:

- Use semantic sections and a top-level `<main class="app-shell">`.
- Connect headings to sections with `aria-labelledby` where applicable.
  - Example: manual input and history sections have IDs referenced by `aria-labelledby`.
- Use real `<button>` elements with `type="button"` for interactions.
- Disable buttons while generation/drawing is in progress to prevent duplicate actions.
- Use `aria-live="polite"` on the deck stage so draw result changes are not overly disruptive.
- Mark decorative symbols with `aria-hidden="true"` where needed.

Maintain these patterns when adding interactive UI.

---

## Common Mistakes

- Do not move reusable parsing or validation logic into template expressions; use `src/lib/choices.ts`.
- Do not add component props before there is an actual child component.
- Do not use anchor tags for button behavior.
- Do not rely only on animation state for disabled behavior; bind `:disabled` for generating/drawing flows.
- Do not create new global CSS naming styles; stay with kebab-case classes and existing visual tokens.
