export type ChoiceSource = 'manual' | 'food' | 'play' | 'movie' | 'drink'

export type AiCategory = 'food' | 'play' | 'drink'
export type GeneratedCategory = Exclude<ChoiceSource, 'manual'>

export type MovieOptionItem = {
  label: string
  movieId?: string | null
  poster?: string | null
  type?: string | null
  actors?: string | null
  releaseDate?: string | null
  score?: string | null
  detailUrl?: string | null
}

export type ChoiceCardSet = {
  id: string
  source: ChoiceSource
  sourceLabel: string
  options: string[]
  aiGenerated: boolean
  items?: MovieOptionItem[]
  createdAt: string
}

export type GeneratedOptionResponse = {
  category: GeneratedCategory
  options: string[]
  items?: MovieOptionItem[]
}

export type ApiErrorResponse = {
  detail?: string
  message?: string
}
