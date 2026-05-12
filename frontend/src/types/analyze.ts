export interface Suggestion {
  title: string
  detail: string
}

export interface AnalyzeResponse {
  match_score: number
  summary: string
  matches: string[]
  gaps: string[]
  suggestions: Suggestion[]
  cached: boolean
}

export interface StatsResponse {
  total_analyses: number
  average_score: number
}
