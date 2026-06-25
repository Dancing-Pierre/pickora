import type { AiCategory, AiOptionResponse, ApiErrorResponse } from '../types/choice'

const CATEGORY_LABELS: Record<AiCategory, string> = {
  food: '吃什么',
  play: '去哪玩',
  movie: '看什么剧/电影'
}

export async function generateOptions(category: AiCategory): Promise<AiOptionResponse> {
  const response = await fetch('/api/generate-options', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ category })
  })

  if (!response.ok) {
    let message = 'AI 生成暂时失败，可以先手动输入选项。'
    try {
      const payload = (await response.json()) as ApiErrorResponse
      message = payload.detail || payload.message || message
    } catch {
      // Keep the generic message for non-JSON failures.
    }
    if (response.status === 429) {
      message = 'AI 生成太频繁了，稍等一下再试，或者先手动输入选项。'
    }
    throw new Error(message)
  }

  const data = (await response.json()) as AiOptionResponse
  if (!Array.isArray(data.options) || data.options.length !== 6) {
    throw new Error(`${CATEGORY_LABELS[category]} 的 AI 结果格式不对，请稍后再试。`)
  }
  return data
}
