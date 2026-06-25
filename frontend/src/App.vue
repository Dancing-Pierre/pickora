<template>
  <main class="app-shell">
    <section class="hero-card">
      <p class="eyebrow">Pickora · 选择抽卡机</p>
      <h1>别纠结了，抽一张。</h1>
      <p class="hero-copy">输入几个选项，或者让 AI 给你凑 6 张卡。翻牌的一瞬间，今天就这么定。</p>
    </section>

    <section class="panel scene-panel" aria-labelledby="ai-title">
      <div class="section-heading">
        <span>AI 快速出牌</span>
        <small>点一下分类，直接生成 6 个候选</small>
      </div>
      <div class="scene-grid" id="ai-title">
        <button
          v-for="scene in scenes"
          :key="scene.category"
          class="scene-button"
          type="button"
          :disabled="isGenerating || isDrawing"
          @click="generateByCategory(scene.category)"
        >
          <span class="scene-icon">{{ scene.icon }}</span>
          <span>{{ scene.label }}</span>
        </button>
      </div>
      <p v-if="aiMessage" class="message" :class="{ error: aiMessageType === 'error' }">{{ aiMessage }}</p>
    </section>

    <section class="panel input-panel" aria-labelledby="manual-title">
      <div class="section-heading">
        <span id="manual-title">自己写选项</span>
        <small>支持粘贴，也支持一个个加</small>
      </div>

      <textarea
        v-model="rawOptions"
        class="option-textarea"
        rows="4"
        placeholder="例如：黄焖鸡 兰溪手擀面 麻辣烫\n也可以用逗号、顿号、换行分隔"
      />
      <div class="input-actions">
        <button class="ghost-button" type="button" @click="applyPastedOptions">解析粘贴内容</button>
        <button class="ghost-button danger" type="button" @click="clearOptions">清空</button>
      </div>

      <div class="tag-add-row">
        <input
          v-model="tagInput"
          class="tag-input"
          type="text"
          maxlength="24"
          placeholder="单独添加一个选项"
          @keydown.enter.prevent="addTagOption"
        />
        <button class="primary-button compact" type="button" @click="addTagOption">添加</button>
      </div>

      <div v-if="options.length" class="option-tags" aria-label="当前选项">
        <button v-for="option in options" :key="option" class="option-tag" type="button" @click="removeOption(option)">
          {{ option }} <span aria-hidden="true">×</span>
        </button>
      </div>

      <p class="helper-text" :class="{ error: Boolean(optionError) }">
        {{ optionError || `当前 ${options.length} 张卡，最多可重抽 ${redrawLimit} 次。` }}
      </p>
    </section>

    <section class="deck-stage" aria-live="polite">
      <div class="stage-orbit stage-orbit-one"></div>
      <div class="stage-orbit stage-orbit-two"></div>

      <div ref="deckRef" class="card-grid" :class="{ drawing: isDrawing }">
        <article v-for="(option, index) in options" :key="`${option}-${index}`" class="choice-card">
          <div class="card-inner">
            <div class="card-face card-back">
              <span class="card-mark">P</span>
              <span class="card-pattern"></span>
            </div>
            <div class="card-face card-front">
              <small>Pickora</small>
              <strong>{{ option }}</strong>
            </div>
          </div>
        </article>
      </div>

      <div v-if="!options.length" class="empty-deck">
        <span>♠</span>
        <p>先给我 3 到 12 个选项，或者点上面的 AI 分类。</p>
      </div>
    </section>

    <section class="result-panel panel">
      <div v-if="result" class="result-card">
        <span class="result-label">命运翻牌</span>
        <strong>{{ result }}</strong>
        <p>已抽 {{ drawCount }} 次 · 已重抽 {{ usedRedraws }} 次 · 还可重抽 {{ remainingRedraws }} 次</p>
      </div>
      <div v-else class="result-placeholder">结果会在这里亮出来。</div>

      <div class="draw-actions">
        <button class="primary-button" type="button" :disabled="Boolean(optionError) || isDrawing" @click="startDraw">
          {{ result ? '重新开始抽卡' : '开始抽卡' }}
        </button>
        <button class="secondary-button" type="button" :disabled="!result || remainingRedraws <= 0 || isDrawing" @click="redraw">
          重抽一次
        </button>
      </div>
    </section>

    <section class="panel history-panel" aria-labelledby="history-title">
      <div class="section-heading">
        <span id="history-title">最近 5 次</span>
        <button v-if="history.length" class="text-button" type="button" @click="clearHistory">清除</button>
      </div>
      <div v-if="history.length" class="history-list">
        <button v-for="session in history" :key="session.id" class="history-item" type="button" @click="reuseSession(session)">
          <span>{{ session.sourceLabel }} · {{ session.finalResult }}</span>
          <small>{{ formatDate(session.createdAt) }} · {{ session.options.length }} 张卡</small>
        </button>
      </div>
      <p v-else class="helper-text">抽完以后，会把完整选项组存在这里，方便下次复用。</p>
    </section>

    <footer class="site-footer">
      <a href="https://www.ansion.top/" target="_blank" rel="noreferrer">暗蚀工研科技 · 专业全栈技术服务</a>
      <span>|</span>
      <span>© 2026 ansion.top · 保留所有权利</span>
      <span>|</span>
      <span>浙ICP备2025172295号-1</span>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { gsap } from 'gsap'
import { generateOptions } from './lib/api'
import { getRedrawLimit, normalizeOptions, parseOptions, pickRandomOption, validateOptionCount } from './lib/choices'
import { useChoiceHistory } from './composables/useChoiceHistory'
import type { AiCategory, ChoiceSession, ChoiceSource } from './types/choice'

const scenes: Array<{ category: AiCategory; label: string; icon: string }> = [
  { category: 'food', label: '吃什么', icon: '🍜' },
  { category: 'play', label: '去哪玩', icon: '🎡' },
  { category: 'movie', label: '看什么剧/电影', icon: '🎬' }
]

const sourceLabels: Record<ChoiceSource, string> = {
  manual: '手动输入',
  food: '吃什么',
  play: '去哪玩',
  movie: '看什么剧/电影'
}

const rawOptions = ref('')
const tagInput = ref('')
const options = ref<string[]>([])
const currentSource = ref<ChoiceSource>('manual')
const currentAiGenerated = ref(false)
const result = ref('')
const drawCount = ref(0)
const usedRedraws = ref(0)
const isDrawing = ref(false)
const isGenerating = ref(false)
const aiMessage = ref('')
const aiMessageType = ref<'info' | 'error'>('info')
const deckRef = ref<HTMLElement | null>(null)

const { history, addSession, clearHistory } = useChoiceHistory()

const optionError = computed(() => (options.value.length ? validateOptionCount(options.value) : '先准备 3 到 12 张卡。'))
const redrawLimit = computed(() => (options.value.length ? getRedrawLimit(options.value.length) : 0))
const remainingRedraws = computed(() => Math.max(0, redrawLimit.value - usedRedraws.value))

function resetResult() {
  result.value = ''
  drawCount.value = 0
  usedRedraws.value = 0
}

function setOptions(nextOptions: string[], source: ChoiceSource, aiGenerated: boolean) {
  options.value = normalizeOptions(nextOptions)
  currentSource.value = source
  currentAiGenerated.value = aiGenerated
  rawOptions.value = options.value.join(' ')
  resetResult()
}

function applyPastedOptions() {
  setOptions(parseOptions(rawOptions.value), 'manual', false)
  aiMessage.value = ''
}

function addTagOption() {
  const next = tagInput.value.trim()
  if (!next) return
  setOptions([...options.value, next], 'manual', false)
  tagInput.value = ''
}

function removeOption(option: string) {
  setOptions(options.value.filter((item) => item !== option), currentSource.value, currentAiGenerated.value)
}

function clearOptions() {
  rawOptions.value = ''
  tagInput.value = ''
  options.value = []
  currentSource.value = 'manual'
  currentAiGenerated.value = false
  resetResult()
}

async function generateByCategory(category: AiCategory) {
  isGenerating.value = true
  aiMessage.value = '正在洗牌，AI 正在塞入 6 张卡…'
  aiMessageType.value = 'info'
  try {
    const data = await generateOptions(category)
    setOptions(data.options, category, true)
    aiMessage.value = `${sourceLabels[category]} 已生成 6 张卡。`
    aiMessageType.value = 'info'
  } catch (error) {
    aiMessage.value = error instanceof Error ? error.message : 'AI 生成暂时失败，可以先手动输入选项。'
    aiMessageType.value = 'error'
  } finally {
    isGenerating.value = false
  }
}

function createSession(finalResult: string): ChoiceSession {
  return {
    id: typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`,
    source: currentSource.value,
    sourceLabel: sourceLabels[currentSource.value],
    options: [...options.value],
    aiGenerated: currentAiGenerated.value,
    finalResult,
    drawCount: drawCount.value,
    redrawCount: usedRedraws.value,
    createdAt: new Date().toISOString()
  }
}

async function playDrawAnimation(selected: string) {
  await nextTick()
  const cards = Array.from(deckRef.value?.querySelectorAll<HTMLElement>('.choice-card') ?? [])
  if (!cards.length) return

  const selectedIndex = Math.max(0, options.value.indexOf(selected))
  const selectedCard = cards[selectedIndex] ?? cards[0]

  gsap.killTweensOf(cards)
  gsap.set(cards, { clearProps: 'all' })
  gsap.set(cards.map((card) => card.querySelector('.card-inner')), { rotateY: 0 })

  const timeline = gsap.timeline()
  timeline
    .to(cards, {
      y: () => gsap.utils.random(-22, 22),
      x: () => gsap.utils.random(-18, 18),
      rotation: () => gsap.utils.random(-12, 12),
      scale: 0.94,
      duration: 0.28,
      stagger: 0.025,
      ease: 'power2.inOut'
    })
    .to(cards, {
      y: 0,
      x: 0,
      rotation: 0,
      scale: 1,
      duration: 0.36,
      stagger: 0.018,
      ease: 'back.out(1.7)'
    })
    .to(cards.filter((card) => card !== selectedCard), {
      opacity: 0.38,
      scale: 0.9,
      duration: 0.24,
      ease: 'power2.out'
    })
    .to(selectedCard, {
      y: -24,
      scale: 1.12,
      rotation: 0,
      duration: 0.32,
      ease: 'power3.out'
    }, '<')
    .to(selectedCard.querySelector('.card-inner'), {
      rotateY: 180,
      duration: 0.62,
      ease: 'power4.inOut'
    })
    .to(selectedCard, {
      boxShadow: '0 0 52px rgba(255, 214, 102, 0.88)',
      duration: 0.28,
      yoyo: true,
      repeat: 1
    })

  await timeline.then()
}

async function drawCard(isRedraw = false) {
  if (optionError.value || isDrawing.value) return
  if (isRedraw && remainingRedraws.value <= 0) return

  if (!isRedraw) {
    usedRedraws.value = 0
    drawCount.value = 0
  } else {
    usedRedraws.value += 1
  }

  drawCount.value += 1
  isDrawing.value = true
  const selected = pickRandomOption(options.value)
  await playDrawAnimation(selected)
  result.value = selected
  addSession(createSession(selected))
  isDrawing.value = false
}

function startDraw() {
  void drawCard(false)
}

function redraw() {
  void drawCard(true)
}

function reuseSession(session: ChoiceSession) {
  setOptions(session.options, session.source, session.aiGenerated)
  aiMessage.value = `已复用「${session.sourceLabel}」这组卡。`
  aiMessageType.value = 'info'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}
</script>
