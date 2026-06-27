import { ref } from 'vue'
import type { ChoiceCardSet, ChoiceSource, MovieOptionItem } from '../types/choice'

const STORAGE_KEY = 'pickora:history:v1'
const MAX_HISTORY = 5
const SIGNATURE_SEPARATOR = '::'

type StoredCardSet = Partial<ChoiceCardSet> & {
  finalResult?: string
  drawCount?: number
  redrawCount?: number
}

export function createCardSetSignature(source: ChoiceSource, options: string[]): string {
  return `${source}|${options.join(SIGNATURE_SEPARATOR)}`
}

function isChoiceSource(value: unknown): value is ChoiceSource {
  return value === 'manual' || value === 'food' || value === 'play' || value === 'movie' || value === 'drink'
}

function normalizeMovieItems(value: unknown): MovieOptionItem[] | undefined {
  if (!Array.isArray(value)) return undefined

  const items = value
    .map((item): MovieOptionItem | null => {
      if (!item || typeof item !== 'object') return null

      const candidate = item as Record<string, unknown>
      if (typeof candidate.label !== 'string' || !candidate.label.trim()) return null

      return {
        label: candidate.label.trim(),
        movieId: typeof candidate.movieId === 'string' ? candidate.movieId : null,
        poster: typeof candidate.poster === 'string' ? candidate.poster : null,
        type: typeof candidate.type === 'string' ? candidate.type : null,
        actors: typeof candidate.actors === 'string' ? candidate.actors : null,
        releaseDate: typeof candidate.releaseDate === 'string' ? candidate.releaseDate : null,
        score: typeof candidate.score === 'string' ? candidate.score : null,
        detailUrl: typeof candidate.detailUrl === 'string' ? candidate.detailUrl : null
      }
    })
    .filter((item): item is MovieOptionItem => Boolean(item))

  return items.length ? items : undefined
}

function createId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`
}

function normalizeStoredCardSet(value: unknown): ChoiceCardSet | null {
  if (!value || typeof value !== 'object') return null

  const item = value as StoredCardSet
  const options = Array.isArray(item.options)
    ? item.options
        .filter((option): option is string => typeof option === 'string')
        .map((option) => option.trim())
        .filter(Boolean)
    : []
  if (!options.length) return null
  if (!isChoiceSource(item.source) || !item.sourceLabel) return null

  const normalized: ChoiceCardSet = {
    id: typeof item.id === 'string' ? item.id : createId(),
    source: item.source,
    sourceLabel: item.sourceLabel,
    options,
    aiGenerated: Boolean(item.aiGenerated),
    createdAt: typeof item.createdAt === 'string' ? item.createdAt : new Date().toISOString()
  }

  const items = normalizeMovieItems(item.items)
  if (items) normalized.items = items
  return normalized
}

function readHistory(): ChoiceCardSet[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.map(normalizeStoredCardSet).filter((item): item is ChoiceCardSet => Boolean(item)).slice(0, MAX_HISTORY)
  } catch {
    return []
  }
}

function writeHistory(history: ChoiceCardSet[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
}

export function useChoiceHistory() {
  const history = ref<ChoiceCardSet[]>(readHistory())

  function addCardSet(cardSet: Omit<ChoiceCardSet, 'id' | 'createdAt'>) {
    const signature = createCardSetSignature(cardSet.source, cardSet.options)
    const existing = history.value.find((item) => createCardSetSignature(item.source, item.options) === signature)
    const next: ChoiceCardSet = existing
      ? { ...existing, ...cardSet }
      : {
          ...cardSet,
          id: createId(),
          createdAt: new Date().toISOString()
        }

    history.value = [next, ...history.value.filter((item) => createCardSetSignature(item.source, item.options) !== signature)].slice(0, MAX_HISTORY)
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
