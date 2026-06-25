export type ChoiceSource = 'manual' | 'food' | 'play' | 'movie'

export type ChoiceSession = {
  id: string
  source: ChoiceSource
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
  finalResult: string
  drawCount: number
  redrawCount: number
  createdAt: string
}

export type AiCategory = Exclude<ChoiceSource, 'manual'>

export type AiOptionResponse = {
  category: AiCategory
  options: string[]
}

export type ApiErrorResponse = {
  detail?: string
  message?: string
}
