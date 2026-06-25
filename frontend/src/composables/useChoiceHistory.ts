import { ref } from 'vue'
import type { ChoiceSession } from '../types/choice'

const STORAGE_KEY = 'pickora:history:v1'
const MAX_HISTORY = 5

function readHistory(): ChoiceSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.slice(0, MAX_HISTORY) : []
  } catch {
    return []
  }
}

function writeHistory(history: ChoiceSession[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
}

export function useChoiceHistory() {
  const history = ref<ChoiceSession[]>(readHistory())

  function addSession(session: ChoiceSession) {
    history.value = [session, ...history.value].slice(0, MAX_HISTORY)
    writeHistory(history.value)
  }

  function clearHistory() {
    history.value = []
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    history,
    addSession,
    clearHistory
  }
}
