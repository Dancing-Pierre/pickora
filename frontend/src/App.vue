<template>
  <main class="app-shell">
    <section class="hero-card compact-hero">
      <div>
        <p class="eyebrow">一念 · 选择抽卡机</p>
        <h1>一念之间，抽一张。</h1>
      </div>
      <p class="hero-copy">选一组卡，凭手感翻开今天的答案。</p>
    </section>

    <section class="quick-panel" aria-labelledby="quick-title">
      <div class="quick-heading">
        <span id="quick-title">快速出牌</span>
        <button class="manual-trigger" type="button" @click="manualDrawerOpen = true">
          <PencilLine :size="16" aria-hidden="true" />
          自己写
        </button>
      </div>

      <div class="scene-grid">
        <button
          v-for="scene in scenes"
          :key="scene.category"
          class="scene-button"
          type="button"
          :disabled="isGenerating || isShuffling"
          @click="generateByCategory(scene.category)"
        >
          <component :is="scene.icon" :size="18" aria-hidden="true" />
          <span>{{ scene.label }}</span>
        </button>
      </div>
      <p v-if="aiMessage" class="message" :class="{ error: aiMessageType === 'error' }">{{ aiMessage }}</p>
    </section>

    <section class="deck-stage" aria-live="polite" aria-labelledby="deck-title">
      <div class="deck-toolbar">
        <div>
          <span id="deck-title" class="deck-title">{{ deckTitle }}</span>
          <small>{{ deckHint }}</small>
        </div>
        <button
          v-if="options.length"
          class="shuffle-button"
          type="button"
          :disabled="Boolean(optionError) || isShuffling"
          aria-label="洗牌后重新翻卡"
          @click="shuffleDeck"
        >
          <Shuffle :size="15" aria-hidden="true" />
          洗牌
        </button>
      </div>

      <div v-if="options.length" ref="deckRef" class="card-fan" :class="{ 'two-row': isTwoRowFan, 'is-shuffling': isShuffling }">
        <button
          v-for="(option, index) in options"
          :key="`${option}-${index}`"
          class="choice-card"
          type="button"
          :class="{
            flipped: flippedIndex === index,
            locked: flippedIndex !== null,
            selected: flippedIndex === index
          }"
          :style="getCardStyle(index, options.length)"
          :disabled="Boolean(optionError) || isShuffling"
          :aria-label="getCardAriaLabel(option, index)"
          @click="handleCardClick(index)"
        >
          <span class="card-inner">
            <span class="card-face card-back">
              <span class="card-corner top">P</span>
              <span class="card-mark">P</span>
              <span class="card-corner bottom">P</span>
            </span>
            <span class="card-face card-front" :class="{ 'movie-card-front': Boolean(getMovieItem(index)?.poster) }" :style="getCardFrontStyle(index)">
              <span v-if="getMovieItem(index)?.poster" class="movie-card-overlay" aria-hidden="true"></span>
              <small>{{ getMovieItem(index) ? '正在热映' : '你的选择' }}</small>
              <strong :class="{ 'movie-card-title': Boolean(getMovieItem(index)) }">{{ option }}</strong>
              <span v-if="flippedIndex === index && getMovieItem(index)" class="movie-card-hint">再点看详情</span>
            </span>
          </span>
        </button>
      </div>

      <div v-else class="empty-deck">
        <WalletCards :size="42" aria-hidden="true" />
        <p>点上面的分类，或展开“自己写”准备 3 到 12 张卡。</p>
      </div>

      <p class="helper-text deck-message" :class="{ error: Boolean(optionError) }">
        {{ optionError || resultMessage }}
      </p>
    </section>

    <footer class="site-footer">
      <span>一念 · 把选择交给此刻</span>
      <span>|</span>
      <span>© 2026 ansion.top · 保留所有权利</span>
      <span>|</span>
      <span>浙ICP备2025172295号-1</span>
    </footer>

    <button class="history-fab" type="button" aria-label="打开最近卡牌" @click="historyDrawerOpen = true">
      <History :size="22" aria-hidden="true" />
      <span v-if="history.length" class="history-count">{{ history.length }}</span>
    </button>

    <div v-if="manualDrawerOpen" class="drawer-backdrop" @click.self="manualDrawerOpen = false">
      <section class="bottom-drawer" aria-labelledby="manual-title">
        <div class="drawer-heading">
          <div>
            <span id="manual-title">自己写选项</span>
            <small>粘贴或逐个添加，应用后生成一组卡牌。</small>
          </div>
          <button class="icon-button" type="button" aria-label="关闭手动输入" @click="manualDrawerOpen = false">
            <X :size="18" aria-hidden="true" />
          </button>
        </div>

        <textarea
          v-model="rawOptions"
          class="option-textarea"
          rows="3"
          placeholder="例如：黄焖鸡 兰溪手擀面 麻辣烫，也可以用逗号、顿号、换行分隔"
        />

        <div class="tag-add-row">
          <input
            v-model="tagInput"
            class="tag-input"
            type="text"
            maxlength="24"
            placeholder="单独添加一个选项"
            @keydown.enter.prevent="addTagOption"
          />
          <button class="ghost-button compact" type="button" @click="addTagOption">添加</button>
        </div>

        <div v-if="draftOptions.length" class="option-tags" aria-label="待应用选项">
          <button v-for="option in draftOptions" :key="option" class="option-tag" type="button" @click="removeDraftOption(option)">
            {{ option }}
            <X :size="12" aria-hidden="true" />
          </button>
        </div>

        <p class="helper-text" :class="{ error: Boolean(draftError) }">
          {{ draftError || `将生成 ${draftOptions.length} 张卡。` }}
        </p>

        <div class="drawer-actions">
          <button class="ghost-button danger" type="button" @click="clearManualDraft">清空</button>
          <button class="primary-button" type="button" :disabled="Boolean(draftError)" @click="applyManualOptions">应用为卡牌</button>
        </div>
      </section>
    </div>

    <div v-if="historyDrawerOpen" class="drawer-backdrop" @click.self="historyDrawerOpen = false">
      <section class="bottom-drawer history-drawer" aria-labelledby="history-title">
        <div class="drawer-heading">
          <div>
            <span id="history-title">最近 5 组卡牌</span>
            <small>点击任意一组，复用这堆卡继续挑选。</small>
          </div>
          <button class="icon-button" type="button" aria-label="关闭最近卡牌" @click="historyDrawerOpen = false">
            <X :size="18" aria-hidden="true" />
          </button>
        </div>

        <div v-if="history.length" class="history-list">
          <button v-for="cardSet in history" :key="cardSet.id" class="history-item" type="button" @click="reuseCardSet(cardSet)">
            <span>{{ cardSet.sourceLabel }} · {{ cardSet.options.length }} 张卡</span>
            <small>{{ cardSet.options.slice(0, 4).join(' / ') }}{{ cardSet.options.length > 4 ? '…' : '' }}</small>
          </button>
        </div>
        <p v-else class="helper-text">还没有保存过卡牌组。生成或应用一组卡后会出现在这里。</p>

        <button v-if="history.length" class="text-button danger" type="button" @click="clearHistory">清除历史</button>
      </section>
    </div>

    <div v-if="movieDetailOpen && selectedMovieItem" class="drawer-backdrop" @click.self="movieDetailOpen = false">
      <section class="bottom-drawer movie-detail-drawer" aria-labelledby="movie-detail-title">
        <div class="drawer-heading">
          <div>
            <span id="movie-detail-title">电影详情</span>
            <small>来自正在热映影片数据。</small>
          </div>
          <button class="icon-button" type="button" aria-label="关闭电影详情" @click="movieDetailOpen = false">
            <X :size="18" aria-hidden="true" />
          </button>
        </div>

        <div class="movie-detail-card">
          <img v-if="selectedMovieItem.poster" class="movie-detail-poster" :src="selectedMovieItem.poster" :alt="`${selectedMovieItem.label} 海报`" />
          <div class="movie-detail-info">
            <strong>{{ selectedMovieItem.label }}</strong>
            <span v-if="selectedMovieItem.score" class="movie-score">评分 {{ selectedMovieItem.score }}</span>
            <p v-if="selectedMovieItem.type">类型：{{ selectedMovieItem.type }}</p>
            <p v-if="selectedMovieItem.actors">主演：{{ selectedMovieItem.actors }}</p>
            <p v-if="selectedMovieItem.releaseDate">上映：{{ selectedMovieItem.releaseDate }}</p>
            <a v-if="selectedMovieItem.detailUrl" class="movie-detail-link" :href="selectedMovieItem.detailUrl" target="_blank" rel="noreferrer">
              查看猫眼详情
            </a>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import type { Component, StyleValue } from 'vue'
import { Clapperboard, Coffee, History, MapPin, PencilLine, Shuffle, Utensils, WalletCards, X } from 'lucide-vue-next'
import { gsap } from 'gsap'
import { generateOptions } from './lib/api'
import { normalizeOptions, parseOptions, validateOptionCount } from './lib/choices'
import { useChoiceHistory } from './composables/useChoiceHistory'
import type { ChoiceCardSet, ChoiceSource, GeneratedCategory, MovieOptionItem } from './types/choice'

type Scene = {
  category: GeneratedCategory
  label: string
  icon: Component
}

const scenes: Scene[] = [
  { category: 'food', label: '吃什么', icon: Utensils },
  { category: 'drink', label: '喝什么', icon: Coffee },
  { category: 'play', label: '去哪玩', icon: MapPin },
  { category: 'movie', label: '看什么', icon: Clapperboard }
]

const sourceLabels: Record<ChoiceSource, string> = {
  manual: '手动输入',
  food: '吃什么',
  drink: '喝什么',
  play: '去哪玩',
  movie: '看什么'
}

const rawOptions = ref('')
const tagInput = ref('')
const options = ref<string[]>([])
const optionItems = ref<MovieOptionItem[]>([])
const currentSource = ref<ChoiceSource>('manual')
const currentAiGenerated = ref(false)
const result = ref('')
const flippedIndex = ref<number | null>(null)
const isShuffling = ref(false)
const isGenerating = ref(false)
const aiMessage = ref('')
const aiMessageType = ref<'info' | 'error'>('info')
const manualDrawerOpen = ref(false)
const historyDrawerOpen = ref(false)
const movieDetailOpen = ref(false)
const deckRef = ref<HTMLElement | null>(null)

const { history, addCardSet, clearHistory } = useChoiceHistory()

const optionError = computed(() => (options.value.length ? validateOptionCount(options.value) : '先准备 3 到 12 张卡。'))
const draftOptions = computed(() => parseOptions(rawOptions.value))
const draftError = computed(() => (draftOptions.value.length ? validateOptionCount(draftOptions.value) : '先写 3 到 12 个选项。'))
const isTwoRowFan = computed(() => options.value.length > 7)
const selectedMovieItem = computed(() => (flippedIndex.value === null ? null : getMovieItem(flippedIndex.value)))
const deckTitle = computed(() => (result.value ? `翻到了：${result.value}` : options.value.length ? '选一张翻开' : '准备你的卡牌'))
const deckHint = computed(() => {
  if (!options.value.length) return '生成或手动输入都可以。'
  if (result.value) return selectedMovieItem.value ? '想看详情再点卡牌，想再选一次就洗牌。' : '想再选一次就点右侧洗牌。'
  return `${options.value.length} 张卡已就位，凭手感点一张。`
})
const resultMessage = computed(() => {
  if (!options.value.length) return '先准备一组卡牌。'
  if (result.value) return selectedMovieItem.value ? `这轮结果是「${result.value}」，再点卡牌看详情。` : `这轮结果是「${result.value}」。`
  return '点击任意一张牌，翻开后本轮会锁定结果。'
})

function getMovieItem(index: number): MovieOptionItem | null {
  return optionItems.value[index] ?? null
}

function normalizeItemsForOptions(nextOptions: string[], items: MovieOptionItem[] = []): MovieOptionItem[] {
  if (items.length === nextOptions.length) return [...items]

  return nextOptions
    .map((option) => items.find((item) => item.label === option) ?? null)
    .filter((item): item is MovieOptionItem => Boolean(item))
}

function resetRound() {
  result.value = ''
  flippedIndex.value = null
  movieDetailOpen.value = false
}

function saveCurrentCardSet() {
  if (validateOptionCount(options.value)) return
  addCardSet({
    source: currentSource.value,
    sourceLabel: sourceLabels[currentSource.value],
    options: [...options.value],
    aiGenerated: currentAiGenerated.value,
    items: optionItems.value.length ? [...optionItems.value] : undefined
  })
}

function setOptions(nextOptions: string[], source: ChoiceSource, aiGenerated: boolean, saveHistory = true, items: MovieOptionItem[] = []) {
  options.value = normalizeOptions(nextOptions)
  optionItems.value = normalizeItemsForOptions(options.value, items)
  currentSource.value = source
  currentAiGenerated.value = aiGenerated
  rawOptions.value = options.value.join(' ')
  resetRound()
  if (saveHistory) saveCurrentCardSet()
}

function addTagOption() {
  const next = tagInput.value.trim()
  if (!next) return
  rawOptions.value = [...draftOptions.value, next].join(' ')
  tagInput.value = ''
}

function removeDraftOption(option: string) {
  rawOptions.value = draftOptions.value.filter((item) => item !== option).join(' ')
}

function clearManualDraft() {
  rawOptions.value = ''
  tagInput.value = ''
}

function applyManualOptions() {
  if (draftError.value) return
  setOptions(draftOptions.value, 'manual', false)
  aiMessage.value = ''
  manualDrawerOpen.value = false
}

async function generateByCategory(category: GeneratedCategory) {
  isGenerating.value = true
  aiMessage.value = '正在洗牌，正在塞入 6 张卡…'
  aiMessageType.value = 'info'
  try {
    const data = await generateOptions(category)
    setOptions(data.options, category, category !== 'movie', true, data.items)
    aiMessage.value = `${sourceLabels[category]} 已生成 6 张卡。`
    aiMessageType.value = 'info'
  } catch (error) {
    aiMessage.value = error instanceof Error ? error.message : '生成选项暂时失败，可以先手动输入选项。'
    aiMessageType.value = 'error'
  } finally {
    isGenerating.value = false
  }
}

function getCardStyle(index: number, total: number): StyleValue {
  const twoRows = total > 7
  const firstRowCount = twoRows ? Math.ceil(total / 2) : total
  const rowIndex = twoRows && index >= firstRowCount ? 1 : 0
  const rowStart = rowIndex === 0 ? 0 : firstRowCount
  const rowCount = rowIndex === 0 ? firstRowCount : total - firstRowCount
  const localIndex = index - rowStart
  const center = (rowCount - 1) / 2
  const rotationStep = twoRows ? 12 : Math.min(16, 78 / Math.max(rowCount - 1, 1))
  const xStep = twoRows ? 42 : 46
  const rotate = (localIndex - center) * rotationStep + (twoRows ? (rowIndex === 0 ? -4 : 4) : 0)
  const x = (localIndex - center) * xStep
  const arc = Math.abs(localIndex - center) * (twoRows ? 5 : 8)
  const y = twoRows ? (rowIndex === 0 ? -50 : 64) + arc : arc
  const z = 30 + rowIndex * 20 + localIndex

  return {
    '--card-rotate': `${rotate}deg`,
    '--card-x': `${x}px`,
    '--card-y': `${y}px`,
    '--card-z': `${z}`
  }
}

function getCardFrontStyle(index: number): StyleValue {
  const movieItem = getMovieItem(index)
  if (!movieItem?.poster) return {}
  return {
    '--movie-poster': `url("${movieItem.poster.replace(/"/g, '%22')}")`
  }
}

function getCardAriaLabel(option: string, index: number): string {
  if (flippedIndex.value === index && getMovieItem(index)) return `查看电影详情：${option}`
  if (flippedIndex.value === index) return `已翻开：${option}`
  return `翻开第 ${index + 1} 张卡`
}

function handleCardClick(index: number) {
  if (optionError.value || isShuffling.value) return
  if (flippedIndex.value === null) {
    flippedIndex.value = index
    result.value = options.value[index]
    return
  }

  if (flippedIndex.value === index && getMovieItem(index)) {
    movieDetailOpen.value = true
  }
}

function readCardNumber(card: HTMLElement, name: string): number {
  const raw = getComputedStyle(card).getPropertyValue(name).trim()
  return Number.parseFloat(raw) || 0
}

function shuffleCurrentCards() {
  const pairs = options.value.map((option, index) => ({
    option,
    item: optionItems.value[index]
  }))

  for (let index = pairs.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1))
    const current = pairs[index]
    pairs[index] = pairs[swapIndex]
    pairs[swapIndex] = current
  }

  options.value = pairs.map((pair) => pair.option)
  optionItems.value = pairs.map((pair) => pair.item).filter((item): item is MovieOptionItem => Boolean(item))
}

function wait(duration: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, duration)
  })
}

async function shuffleDeck() {
  if (optionError.value || isShuffling.value) return
  isShuffling.value = true
  resetRound()
  await nextTick()

  const cards = Array.from(deckRef.value?.querySelectorAll<HTMLElement>('.choice-card') ?? [])
  gsap.killTweensOf(cards)
  gsap.set(cards, {
    '--shuffle-x': '0px',
    '--shuffle-y': '0px',
    '--shuffle-rotate': '0deg',
    '--card-scale': 1
  })

  await gsap.to(cards, {
    '--shuffle-x': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-x')}px`,
    '--shuffle-y': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-y') + 34}px`,
    '--shuffle-rotate': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-rotate')}deg`,
    duration: 0.38,
    ease: 'power2.inOut',
    stagger: 0,
    overwrite: 'auto'
  })

  await wait(500)
  shuffleCurrentCards()
  await nextTick()

  const nextCards = Array.from(deckRef.value?.querySelectorAll<HTMLElement>('.choice-card') ?? [])
  gsap.killTweensOf(nextCards)
  gsap.set(nextCards, {
    '--shuffle-x': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-x')}px`,
    '--shuffle-y': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-y') + 34}px`,
    '--shuffle-rotate': (_index: number, card: HTMLElement) => `${-readCardNumber(card, '--card-rotate')}deg`,
    '--card-scale': 1
  })

  await gsap.to(nextCards, {
    '--shuffle-x': '0px',
    '--shuffle-y': '0px',
    '--shuffle-rotate': '0deg',
    duration: 0.28,
    ease: 'linear',
    stagger: 0,
    overwrite: 'auto'
  })

  gsap.killTweensOf(nextCards)
  gsap.set(nextCards, {
    '--shuffle-x': '0px',
    '--shuffle-y': '0px',
    '--shuffle-rotate': '0deg',
    '--card-scale': 1
  })
  isShuffling.value = false
}

function reuseCardSet(cardSet: ChoiceCardSet) {
  setOptions(cardSet.options, cardSet.source, cardSet.aiGenerated, true, cardSet.items)
  aiMessage.value = `已复用「${cardSet.sourceLabel}」这组卡。`
  aiMessageType.value = 'info'
  historyDrawerOpen.value = false
}
</script>
