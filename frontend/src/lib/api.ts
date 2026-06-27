import type { ApiErrorResponse, GeneratedCategory, GeneratedOptionResponse, MovieOptionItem } from '../types/choice'

const CATEGORY_LABELS: Record<GeneratedCategory, string> = {
  food: '吃什么',
  play: '去哪玩',
  movie: '看什么',
  drink: '喝什么'
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

export async function generateOptions(category: GeneratedCategory): Promise<GeneratedOptionResponse> {
  const response = await fetch('/api/generate-options', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ category })
  })

  if (!response.ok) {
    let message = '生成选项暂时失败，可以先手动输入选项。'
    try {
      const payload = (await response.json()) as ApiErrorResponse
      message = payload.detail || payload.message || message
    } catch {
      // Keep the generic message for non-JSON failures.
    }
    if (response.status === 429) {
      message = '生成太频繁了，稍等一下再试，或者先手动输入选项。'
    }
    throw new Error(message)
  }

  const data = (await response.json()) as GeneratedOptionResponse
  if (!Array.isArray(data.options) || data.options.length !== 6) {
    throw new Error(`${CATEGORY_LABELS[category]} 的结果格式不对，请稍后再试。`)
  }

  return {
    category: data.category,
    options: data.options,
    items: normalizeMovieItems(data.items)
  }
}
