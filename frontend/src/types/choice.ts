export type ChoiceSource = 'manual' | 'food' | 'play' | 'movie'

export type ChoiceCardSet = {
  id: string
  source: ChoiceSource
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
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
