import { apiClient } from './client'
import type { AnalyzeResponse } from '@/types/analyze'

export async function analyzeMatch(cv: File, jobPosting: string): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('cv', cv)
  formData.append('job_posting', jobPosting)

  const { data } = await apiClient.post<AnalyzeResponse>('/api/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
