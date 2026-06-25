const SPLIT_PATTERN = /[\n\r,，、;；|/\\\t ]+/g

export function normalizeOptions(values: string[]): string[] {
  const seen = new Set<string>()
  const normalized: string[] = []

  for (const value of values) {
    const trimmed = value.trim()
    if (!trimmed || seen.has(trimmed)) continue
    seen.add(trimmed)
    normalized.push(trimmed)
  }

  return normalized
}

export function parseOptions(input: string): string[] {
  return normalizeOptions(input.split(SPLIT_PATTERN))
}

export function validateOptionCount(options: string[]): string | null {
  if (options.length < 3) return '至少需要 3 个选项，才有抽卡的感觉。'
  if (options.length > 12) return '最多支持 12 个选项，先帮我精简一下吧。'
  return null
}

export function getRedrawLimit(cardCount: number): number {
  return Math.max(1, Math.floor(cardCount / 3))
}

export function pickRandomOption(options: string[]): string {
  if (options.length === 0) return ''
  const index = Math.floor(Math.random() * options.length)
  return options[index]
}
